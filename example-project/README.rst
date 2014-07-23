cronkite Example Project
========================

This is an example django project utilizing ``cronkite`` and creates a couple of jobs. It includes
an almost-empty app, ``walter``.

The Important Bits
------------------

Refer to ``project/walter/admin.py`` to see options for utilizing the optional ``Job.auto_discover()`` method.

Tasks are defined in ``project.walter.crontab``.

``settings.py`` includes a logger config that pushes ``cronkite`` messages to console.

Running The Example
-------------------

.. code:: bash

   user@host:~/django-cronkite$ mkvirtualenv cronkite
   user@host:~/django-cronkite$ pip install django
   user@host:~/django-cronkite$ pip install -r requirements.txt
   user@host:~/django-cronkite$ cd example-project
   user@host:~/django-cronkite$ ./manage.py syncdb
   user@host:~/django-cronkite$ ./manage.py runserver &
   user@host:~/django-cronkite$ curl http://localhost:8000/

