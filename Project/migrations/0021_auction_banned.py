# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-17 14:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0020_auto_20171009_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='banned',
            field=models.BooleanField(default=False),
        ),
    ]