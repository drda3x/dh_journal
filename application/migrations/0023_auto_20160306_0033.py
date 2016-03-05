# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0022_auto_20160306_0018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dances',
            options={'verbose_name': '\u0422\u0430\u043d\u0446\u0435\u0432\u0430\u043b\u044c\u043d\u043e\u0435 \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435', 'verbose_name_plural': '\u0422\u0430\u043d\u0446\u0435\u0432\u0430\u043b\u044c\u043d\u044b\u0435 \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f'},
        ),
        migrations.AddField(
            model_name='groups',
            name='end_time',
            field=models.TimeField(default=None, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0437\u0430\u043d\u044f\u0442\u0438\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='dance',
            field=models.ForeignKey(verbose_name='\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435', blank=True, to='application.Dances', null=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='level',
            field=models.ForeignKey(verbose_name='\u0423\u0440\u043e\u0432\u0435\u043d\u044c', blank=True, to='application.GroupLevels', null=True),
        ),
    ]
