# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 23:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0003_auto_20171112_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='version',
            field=models.DecimalField(decimal_places=1, default=0.1, max_digits=10),
        ),
    ]
