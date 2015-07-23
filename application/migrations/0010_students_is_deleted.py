# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_auto_20150722_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d'),
        ),
    ]
