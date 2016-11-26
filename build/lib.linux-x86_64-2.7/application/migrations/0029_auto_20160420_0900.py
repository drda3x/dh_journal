# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_auto_20160419_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancehalls',
            name='lat',
            field=models.FloatField(null=True, verbose_name='\u0428\u0438\u0440\u043e\u0442\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='dancehalls',
            name='lon',
            field=models.FloatField(null=True, verbose_name='\u0414\u043e\u043b\u0433\u043e\u0442\u0430', blank=True),
        ),
    ]
