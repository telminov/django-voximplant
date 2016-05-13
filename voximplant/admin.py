# coding: utf-8
from django.contrib import admin
from . import models

admin.site.register(models.Application)
admin.site.register(models.Rule)
admin.site.register(models.Scenario)
