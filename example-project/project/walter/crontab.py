# example-project/project/walter/crontab.py
#   -- django-cronkite example tasks
#
# Note that the the 'schedule' property isn't required unless you're using Job.auto_discover().


def send_queued_mail(processes=1):
    """
    Send all email queued by django-post_office once a minute.
    """
    from post_office.mail import send_queued
    send_queued(processes)
send_queued_mail.schedule = '* * * * * *'


def purge_old_cronkite_logs(days, node_list=None):
    """
    Purge cronkite logs older than some days, optionally for specific nodes,
    at midnight on the first day of each month.
    """
    from cronkite.models import Log
    from datetime import datetime, timedelta

    if not days:
        raise Exception("Please specify a minimum age, in days.")

    # get the list of log entries to delete
    qs = Log.objects.filter(
        created__lte=abs(datetime.now() - timedelta(days=days))
    )

    # if a node_list was provided, limit our selection to the
    # log entries for jobs executed by those hosts.
    if node_list:
        qs = qs.filter(node__in=node_list)

    qs.delete()
purge_old_cronkite_logs.schedule = '0 0 1 * *'
