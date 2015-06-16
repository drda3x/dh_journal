# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0008_auto_20150616_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='passtypes',
            name='color',
            field=models.CharField(max_length=7, null=True, verbose_name='\u0426\u0432\u0435\u0442', blank=True),
        ),
        migrations.AddField(
            model_name='students',
            name='org',
            field=models.BooleanField(default=False, verbose_name='\u041e\u0440\u0433'),
        ),
    ]
