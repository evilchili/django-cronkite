from django.contrib import admin
from cronkite.models import Job

# Option 1:
# create jobs for any new functions in project.crontab, but do not
# delete missing ones or update existing ones.
Job.auto_discover('project.walter.crontab', delete_first=False)

# Option 2:
# Purge all jobs created for functions in project.crontab, then
# create new ones for each function we find therein.
# WARNING: This will discard any changes made in the admin UI!
#Job.auto_discover('project.walter.crontab', delete_first=True)
