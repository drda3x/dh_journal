# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_auto_20160407_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='_external_passes',
            field=models.CommaSeparatedIntegerField(max_length=1000, null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u043d\u0430 \u0432\u043d\u0435\u0448\u043d\u0438\u0445 \u0441\u0430\u0439\u0442\u0430\u0445', blank=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='_available_passes',
            field=models.CommaSeparatedIntegerField(max_length=1000, null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0435\u0439', blank=True),
        ),
    ]
