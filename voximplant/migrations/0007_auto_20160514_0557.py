# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-14 05:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voximplant', '0006_calllist_calllistphone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calllist',
            name='vox_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='calllistphone',
            name='last_attempt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='calllistphone',
            unique_together=set([('call_list', 'phone_number')]),
        ),
    ]
