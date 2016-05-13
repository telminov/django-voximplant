# coding: utf-8
from django.db import models
from django.conf import settings


class Application(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    modified = models.DateTimeField(null=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Rule(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    application = models.ForeignKey(Application)
    name = models.CharField(max_length=255, unique=True)
    pattern = models.CharField(max_length=255, blank=True)
    modified = models.DateTimeField(null=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Scenarios(models.Model):
    vox_id = models.BigIntegerField(null=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    modified = models.DateTimeField(null=True)
    file = models.FilePathField(path=settings.VOX_SCRIPTS_PATH)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

