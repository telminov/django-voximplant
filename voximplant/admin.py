# coding: utf-8
from django.contrib import admin
from . import models

admin.site.register(models.Application)
admin.site.register(models.Rule)
admin.site.register(models.Scenario)


class CallListPhoneInline(admin.StackedInline):
    model = models.CallListPhone
    extra = 1


class CallList(admin.ModelAdmin):
    inlines = (CallListPhoneInline, )
    list_display = ('rule', 'created', 'started', 'completed', 'canceled', 'id', 'vox_id', 'external_id', 'phones')

    def phones(self, obj):
        return obj.phones.count()

admin.site.register(models.CallList, CallList)
