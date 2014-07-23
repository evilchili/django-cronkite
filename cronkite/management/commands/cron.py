from django.core.management.base import BaseCommand
from cronkite.models import Job
import logging

logger = logging.getLogger('cronkite')


class Command(BaseCommand):

    """
    Run all queued cron jobs.
    """

    help = 'Process the jobs and run any that are queued.'

    def handle(self, *args, **options):
        Job.process_queue()
