# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0023_auto_20160306_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclasses',
            name='end_time',
            field=models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='bonusclasses',
            name='time',
            field=models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430', blank=True),
        ),
    ]
