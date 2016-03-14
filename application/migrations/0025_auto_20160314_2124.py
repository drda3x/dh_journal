# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0024_auto_20160312_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='dancehalls',
            name='name',
            field=models.CharField(max_length=50, null=True, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435', blank=True),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='station',
            field=models.CharField(max_length=50, null=True, verbose_name='\u0421\u0442\u0430\u043d\u0446\u0438\u044f \u043c\u0435\u0442\u0440\u043e', blank=True),
        ),
    ]
