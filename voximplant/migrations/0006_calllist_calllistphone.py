# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-14 05:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voximplant', '0005_rule_scenarios'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('vox_id', models.BigIntegerField(null=True, unique=True)),
                ('priority', models.SmallIntegerField(default=1)),
                ('max_simultaneous', models.SmallIntegerField(default=10)),
                ('num_attempts', models.SmallIntegerField(default=3)),
                ('name', models.CharField(max_length=255)),
                ('interval_seconds', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('started', models.DateTimeField(null=True)),
                ('completed', models.DateTimeField(null=True)),
                ('canceled', models.DateTimeField(null=True)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voximplant.Rule')),
            ],
        ),
        migrations.CreateModel(
            name='CallListPhone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11)),
                ('custom_data_json', models.TextField()),
                ('status', models.CharField(blank=True, max_length=50)),
                ('last_attempt', models.DateTimeField()),
                ('attempts_left', models.SmallIntegerField(null=True)),
                ('result_data_json', models.TextField()),
                ('call_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voximplant.CallList')),
            ],
        ),
    ]