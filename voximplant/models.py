# coding: utf-8
import datetime
import os.path
from django.db import models
from django.conf import settings
from django.db.models import Max
from django.utils import timezone


class Scenario(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True)
    uploaded = models.DateTimeField(null=True)
    file_path = models.FilePathField(path=settings.VOX_SCRIPTS_PATH)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def get_script(self):
        with open(self.file_path) as f:
            text = f.read()
        return text

    def get_script_modified(self):
        if not self.file_path:
            return None
        mtime = os.path.getmtime(self.file_path)
        dt = datetime.datetime.fromtimestamp(mtime)
        dt = timezone.make_aware(dt)
        return dt

    def get_modified(self):
        script_modified = self.get_script_modified()
        if script_modified:
            return min([script_modified, self.modified])
        else:
            return self.modified


class Application(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True, blank=True)
    name = models.CharField(max_length=255, unique=True, default='.voximplant.com')
    modified = models.DateTimeField(auto_now=True)
    uploaded = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Rule(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True, blank=True)
    application = models.ForeignKey(Application)
    name = models.CharField(max_length=255, unique=True)
    pattern = models.CharField(max_length=255, default='.*')
    modified = models.DateTimeField(auto_now=True)
    uploaded = models.DateTimeField(null=True, blank=True)
    scenarios = models.ManyToManyField(Scenario, related_name='rules')

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class CallList(models.Model):
    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    vox_id = models.BigIntegerField(null=True, unique=True, blank=True)
    rule = models.ForeignKey(Rule)
    priority = models.SmallIntegerField(default=1)
    max_simultaneous = models.SmallIntegerField(default=10)
    num_attempts = models.SmallIntegerField(default=3)
    name = models.CharField(max_length=255, default='call_list')
    interval_seconds = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    canceled = models.DateTimeField(null=True, blank=True)
    downloaded = models.DateTimeField(null=True, blank=True, help_text='Last datetime of checking state from VoxImplant')

    def completed(self):
        if not self.started:
            return None

        if self.phones.filter(completed__isnull=True).exists():
            return None

        return self.phones.aggregate(latest_completed=Max('completed'))['latest_completed']


class CallListPhone(models.Model):
    STATUS_NEW = 'New'
    STATUS_IN_PROGRESS = 'In progress'
    STATUS_PROCESSED = 'Processed'
    STATUS_ERROR = 'Error'
    STATUS_CHOICES = (
        ('', ''),
        (STATUS_NEW, STATUS_NEW),
        (STATUS_IN_PROGRESS, STATUS_IN_PROGRESS),
        (STATUS_PROCESSED, STATUS_PROCESSED),
        (STATUS_ERROR, STATUS_ERROR),
    )

    call_list = models.ForeignKey(CallList, related_name='phones')
    phone_number = models.CharField(max_length=11)
    custom_data_json = models.TextField()
    status = models.CharField(max_length=50, blank=True, choices=STATUS_CHOICES)
    last_attempt = models.DateTimeField(null=True, blank=True)
    attempts_left = models.SmallIntegerField(null=True, blank=True)
    result_data_json = models.TextField(blank=True)
    completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('call_list', 'phone_number')

    def __str__(self):
        return self.phone_number