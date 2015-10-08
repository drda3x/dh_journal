# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_groups_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='time',
            field=models.TimeField(default=None, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0437\u0430\u043d\u044f\u0442\u0438\u044f', blank=True),
        ),
    ]
