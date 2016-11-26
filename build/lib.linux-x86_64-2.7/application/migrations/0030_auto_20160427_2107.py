# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0029_auto_20160420_0900'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bonusclasses',
            name='_available_groups',
        ),
        migrations.RemoveField(
            model_name='bonusclasses',
            name='_available_passes',
        ),
        migrations.AddField(
            model_name='bonusclasses',
            name='available_groups',
            field=models.ManyToManyField(to='application.Groups', verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0433\u0440\u0443\u043f\u043f\u044b'),
        ),
        migrations.AddField(
            model_name='bonusclasses',
            name='available_passes',
            field=models.ManyToManyField(to='application.PassTypes', verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b'),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='lat',
            field=models.FloatField(null=True, verbose_name='\u0414\u043e\u043b\u0433\u043e\u0442\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='lon',
            field=models.FloatField(null=True, verbose_name='\u0428\u0438\u0440\u043e\u0442\u0430', blank=True),
        ),
    ]
