from django.db import models
from datetime import datetime


class JobManager(models.Manager):

    def queue(self, date=None):
        """
        Return a queryset consisting of jobs that should run now.
        """
        qs = super(JobManager, self).get_query_set()
        return qs.filter(
            next_run__lte=date or datetime.now(),
            lock=None,
            enabled=True,
        )
