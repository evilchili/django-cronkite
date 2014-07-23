from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from croniter import croniter
from cronkite.models import Job, Log


class JobAdminForm(forms.ModelForm):

    def clean_schedule(self):
        s = self.cleaned_data['schedule']
        try:
            croniter(s)
        except Exception as e:
            raise ValidationError("Invalid schedule: %s" % e)

        return self.cleaned_data['schedule']

    class Meta:
        model = Job


class JobAdmin(admin.ModelAdmin):

    form = JobAdminForm

    def is_locked(self, obj):
        return obj.lock is not None
    is_locked.boolean = True

    list_display = (
        "schedule",
        "name",
        "function",
        "args",
        "kwargs",
        "enabled",
        "is_locked"
    )
    list_display_links = ("name", "function", "args", "kwargs")
    readonly_fields = ("next_run", "lock")


class LogAdmin(admin.ModelAdmin):

    def failed(self, obj):
        return obj.exc_info is None
    failed.boolean = True

    list_display = (
        "created",
        "node",
        "job",
        "result",
        "failed"
    )
    readonly_fields = ("node", "job", "result", "exc_info")

admin.site.register(Job, JobAdmin)
admin.site.register(Log, LogAdmin)
