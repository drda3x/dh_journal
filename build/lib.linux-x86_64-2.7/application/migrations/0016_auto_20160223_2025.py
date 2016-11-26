# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0015_auto_20160216_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='e_mail',
            field=models.CharField(max_length=30, null=True, verbose_name='e-mail', blank=True),
        ),
        migrations.AlterField(
            model_name='students',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d'),
        ),
    ]
