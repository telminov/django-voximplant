# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-19 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voximplant', '0012_auto_20160721_0716'),
    ]

    operations = [
        migrations.AddField(
            model_name='calllistphone',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='file_path',
            field=models.FilePathField(path='/home/telminov/git/soft-way/notify/vox_scripts'),
        ),
    ]