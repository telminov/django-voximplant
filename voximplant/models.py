# coding: utf-8
import datetime
import os.path
from django.db import models
from django.conf import settings
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
        mtime = os.path.getmtime(self.file_path)
        dt = datetime.datetime.fromtimestamp(mtime)
        dt = timezone.make_aware(dt)
        return dt

    def get_modified(self):
        script_modified = self.get_script_modified()
        return script_modified if self.modified < script_modified else self.modified


class Application(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Rule(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    application = models.ForeignKey(Application)
    name = models.CharField(max_length=255, unique=True)
    pattern = models.CharField(max_length=255, blank=True)
    modified = models.DateTimeField(auto_now=True)
    scenarios = models.ManyToManyField(Scenario, related_name='rules')

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
