# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0024_groups__available_passes'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='end_date',
            field=models.DateField(default=None, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0433\u0440\u0443\u043f\u043f\u044b', blank=True),
        ),
    ]
