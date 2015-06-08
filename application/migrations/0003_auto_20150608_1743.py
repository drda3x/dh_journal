# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_auto_20150608_1709'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='days',
            options={'verbose_name': '\u0414\u0435\u043d\u044c \u043d\u0435\u0434\u0435\u043b\u0438', 'verbose_name_plural': '\u0414\u043d\u0438 \u043d\u0435\u0434\u0435\u043b\u0438'},
        ),
        migrations.AddField(
            model_name='groups',
            name='is_settable',
            field=models.BooleanField(default=True, verbose_name='\u041d\u0430\u0431\u043e\u0440 \u043e\u0442\u043a\u0440\u044b\u0442'),
        ),
    ]
