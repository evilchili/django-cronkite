django-cronkite
===============

A lightweight distributed cron replacement for django

``django-cronkite`` is a simple, lightweight task runner for django.

Impetus
-------

I wanted a task runner that:

- was safe for a high-availability deployments (advisory locking, no master node)
- was database-agnostic (do not force your favourite rdbms backend on me, thanks)
- had no system-level dependencies (no redis, no custom daemons, no shared filesystems)
- used crontab-compatible scheduling

``django-cronkite`` satisfies these goals at the cost of doing away with vast hunks of functionality you might expect 
in a task runner. In fact about the only thing it *does* do is prevent all your server nodes from running the same 
task more times than they should.

Alternatives
------------

Presumably you landed here because `celery <http://www.celeryproject.org/>`_, `0MQ <http://zeromq.org/>`_, 
`django-rq <https://github.com/ui/django-rq>`_, `huey <https://github.com/coleifer/huey>`_, etc are all 
too big, require extra dependencies, or solve more problems than you have. If not, you should look carefully 
at these packages before proceeding; they are vastly more capable and flexible than ``cronkite``.

Installation
------------

Add ``"cronkite"`` to your ``INSTALLED_APPS`` and run a ``syncdb``.

Optionally, add ``CRONKITE_LOCK_TIMEOUT`` to your ``django.settings``. This is the age, in seconds, at which a job's 
lock will be deemed to have gone stale, and will be cleared by the next run attempt.  

By default (ie, with ``CRONKITE_LOCK_TIMEOUT`` unset, or set to ``None``) a lock is *never* cleared, and locked tasks
will never be retried.

Add a cron job to your server nodes that runs the ``cron`` management command as often as you like (once every minute is 
probably a good idea).

Usage
-----

In the django-admin, create a new ``Job`` record specifying the full dotted name to the function (and optionally, its parameters) 
you wish to run, and the schedule on which to run it.

Each time the ``cron`` management command is run, ``django-cronkite`` will look for any job that is scheduled to run, and 
runs it. The result of the run, including any exception info, is recorded in a ``Log`` record.  Additional logging is 
directed to the 'cronkite' logger; you can add a custom logger entry in ``django.settings`` to handle these messages 
however you like.

Job Auto-Discovery
------------------

Instead of using the Admin UI, you can (re)create Job records automatically using the
Job.auto_discover() class method:

    # app/crontab.py
    function good_morning():
        """ 
        Say good_morning at midnight on Sunday.
        """
        print "Good morning!"
    truth.schedule = '0 0 * * 0'


    # app/admin.py (or wherever):
    from cronkite.models import Job
    Job.auto_discover('app.crontab')

This will create a Job that will execute ``app.crontab.good_morning`` at midnight every Sunday; the 
name of the Job will be ``good_morning``, and the description will be the function's docstring. If 
such a job already exists, no changes will be made.

Note that calling ``auto_discover()`` will not automatically sync the Job records for the specified
module with the current contents of that module. To do, so you must first delete all Job records 
associated with functions in that module. Changing the above example to:

    Job.auto_discover('app.crontab', delete_first=True)

Will delete all existing Jobs associated with ``app.crontab`` and recreate them.  You should
probably only rely on this if you don't want to expose ``django-cronkite`` in the Admin UI.

Example
-------

There is an example django project utilizing ``cronkite`` in the ``example-project`` dir.
