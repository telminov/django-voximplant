# coding: utf-8
from rest_framework import serializers
from . import models


# class CallList(serializers.ModelSerializer):
#     class Meta:
#         model = models.CallList()
#         fields = ('external_id', 'rule', 'priority', 'max_simultaneous', 'num_attempts', 'name', 'interval_seconds')
#         read_only_fields = ('vox_id', 'created', 'started', 'completed', 'canceled')