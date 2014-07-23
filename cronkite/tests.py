from django.test import TestCase
from django.conf import settings
from models import Job, Log
from zope.dottedname.resolve import resolve
from datetime import datetime, timedelta
from cronkite.exceptions import JobIsLocked


def dummy(x=0, y=0, add=True):
    """
    A dummy function designed that adds or subtracsts two variables.
    Used to test the invocation of a scheduled task.
    """
    if add:
        return x + y
    else:
        return x - y


class MixIn(object):

    """
    Common properties and methods for test cases.
    """

    job = None

    def setUp(self):

        self.job = Job(
            function='cronkite.tests.dummy',
            name="Test Function",
            description="A Unit Test Function",
            enabled=True,
            schedule="* * * * * *"
        )
        self.job.save()

    def tearDown(self):
        self.job.delete()


class LogTestCase(MixIn, TestCase):

    """
    Test that the logging works.
    """

    def test_log_creation(self):
        """
        Ensure that a log entry is created after a job runs.
        """
        self.job.run()
        l = Log.objects.get()
        assert(l.job == self.job)


class JobTestCase(MixIn, TestCase):

    """
    Test the cronkite job scheduler.
    """

    def test_create_job(self):
        """
        Test that creating a job accurately stores the full dotted name to the function.
        """
        assert(resolve(self.job.function) == dummy)
        assert(self.job.next_run >= datetime.now())

    def test_queue_after_run(self):
        """
        Test that queuing prevents running the job twice in less than a minute.
        """
        self.job.run()
        assert(len(Job.objects.queue()) == 0)

    def test_run_job_no_args(self):
        """
        Test that the job runs without arguments.
        """
        result = self.job.run()
        assert(result == 0)

    def test_run_job_with_args(self):
        """
        Test that the job runs with args but wihtout keyword args.
        """
        self.job.args = [3, 2]
        self.job.save()
        result = self.job.run()
        assert(result == 5)

    def test_run_job_with_args_and_kwargs(self):
        """
        Test that the job runs with args and keyword args.
        """
        self.job.args = [3, 2]
        self.job.kwargs = {'add': False}
        self.job.save()
        result = self.job.run()
        assert(result == 1)

    def test_queue_no_locks(self):
        """
        Ensure the queue does not ever include locked jobs.
        """
        self.job.lock = datetime.now()
        self.job.save()
        assert(len(Job.objects.queue()) == 0)

    def test_run_fails_when_locked(self):
        """
        Make sure jobs that have a lock timestamp do not run.
        """
        self.job.lock = datetime.now()
        self.job.save()
        try:
            self.job.run()
        except JobIsLocked:
            pass
        else:
            raise

    def test_expired_locks(self):
        """
        Ensure a job will run if its lock has expired.
        """
        threshold = getattr(settings, 'CRONKITE_LOCK_TIMEOUT', 1)
        self.job.lock = datetime.now() - timedelta(seconds=threshold + 1)
        result = self.job.run()
        assert(result == 0)
