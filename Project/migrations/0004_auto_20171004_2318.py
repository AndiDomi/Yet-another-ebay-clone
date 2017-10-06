# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-04 23:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0003_auto_20171004_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='bid',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='bid_res',
            field=models.IntegerField(default=1, null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='details',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2017, 10, 4, 23, 18, 25, 760731), null=True),
        ),
        migrations.AlterField(
            model_name='auction',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]