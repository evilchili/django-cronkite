from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from picklefield.fields import PickledObjectField
from managers import JobManager
from datetime import datetime
from croniter import croniter
from zope.dottedname.resolve import resolve
from cronkite import exceptions
import types
import importlib
import traceback
import os
import sys
import logging

logger = logging.getLogger('cronkite')


class Job(models.Model):

    """
    A model representing a cron-job-alike that uses advisory locking to
    prevent multiple concurrent executions of the same job.
    """

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    function = models.CharField(max_length=254)
    args = PickledObjectField(blank=True)
    kwargs = PickledObjectField(blank=True)
    name = models.CharField(
        max_length=100, null=False, blank=False, db_index=True)
    description = models.CharField(max_length=254, blank=True)

    enabled = models.BooleanField(db_index=True, default=True)
    schedule = models.CharField(
        max_length=30,
        help_text="schedule in <a href='http://en.wikipedia.org/wiki/Cron#Format'>crontab format</a>"
    )
    next_run = models.DateTimeField(db_index=True, null=True, blank=True)
    lock = models.DateTimeField(null=True, blank=True)

    objects = JobManager()

    def run(self):
        """
        Execute the job one time and update the next_run timestamp.
        """

        now = datetime.now()

        # Check to see how long the job has been locked. If there is a timeout
        # configured in django.settings, we will expire the lock if we have
        # exceeded the threshold. Otherwise, the lock remains indefinitely.
        #
        if self.lock:
            threshold = getattr(settings, 'CRONKITE_LOCK_TIMEOUT', None)
            if threshold is None or abs(now - self.lock).seconds < threshold:
                raise exceptions.JobIsLocked

        try:
            self.lock = now
            self.save()
        except Exception as e:
            logger.error(e, exc_info=sys.exc_info())

        # execute the task
        failed = False
        result = None
        args = self.args or []
        kwargs = self.kwargs or {}
        try:
            result = resolve(self.function)(*args, **kwargs)
        except Exception as e:
            logger.error(e, exc_info=sys.exc_info())
            failed = True

        # Determine when the job should run next, based on the schedule,
        # update the next_run timestamp, unlock the job, and log the execution.
        # If any of this fails we throw an exception, preserving the original
        # exception, if any.
        try:
            self.next_run = self.get_next_run(now)
            self.lock = None
            self.save()
            l = Log(job=self, result=result)
            l.exc_info = traceback.format_exc() if failed else None
            l.save()
        except Exception as e:
            logger.error(e, exc_info=sys.exc_info())
            raise

        # no exceptions, so return the result
        return result

    def get_next_run(self, whence=None):
        """
        Return a datetime object for the next time this job should be executed.
        """
        if not whence:
            whence = datetime.now()
        i = croniter(self.schedule, whence)
        return i.get_next(datetime)

    def __unicode__(self):
        return self.name

    @classmethod
    def process_queue(cls):
        """
        Run all jobs that should be run.
        """
        for job in cls.objects.queue():
            job.run()

    @classmethod
    def auto_discover(cls, module_name, delete_first=False):
        """
        Create a Job record for every method in the specified module,
        optionally replacing existing Jobs.
        """

        # attempt to import the specified module
        mod = importlib.import_module(module_name)

        # delete all scheduled jobs associated with this module, if any.
        if delete_first:
            cls.objects.filter(name__startswith=module_name).delete()

        # step through the names in the module
        for name in dir(mod):

            # to create a Job, we must have a function with a schedule property.
            obj = getattr(mod, name, None)
            if not isinstance(obj, types.FunctionType):
                continue
            schedule = getattr(obj, 'schedule', None)
            if not schedule:
                logger.debug("auto_discover: function %s is missing the schedule property." % name)
                continue

            # get or create the job with specified schedule.
            cls.objects.get_or_create(
                name=name,
                function='%s.%s' % (module_name, name),
                defaults={
                    'schedule': obj.schedule,
                    'description': obj.__doc__.strip(),
                }
            )

    class Meta:
        index_together = [['next_run', 'enabled', 'lock']]


class Log(models.Model):

    """
    Log the results of a job's execution, including the host it ran on.
    """

    def current_node():
        """
        Return the current hostname
        """
        return os.uname()[1]

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    node = models.CharField(max_length=254, db_index=True, default=current_node)
    job = models.ForeignKey(Job)
    result = PickledObjectField(null=True, blank=True)
    exc_info = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s %s %s result: %s (%s)" % (
            self.created,
            self.node,
            self.job,
            self.result,
            self.exc_info
        )

    class Meta:
        index_together = [['created', 'node']]


def set_next_run(sender, instance, **kwargs):
    """
    Always compute the next_run time from the schedule.
    """
    instance.next_run = instance.get_next_run()

pre_save.connect(set_next_run, sender=Job)
