# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_auto_20151205_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='sampopayments',
            name='comment',
            field=models.CharField(max_length=50, null=True, verbose_name='\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True),
        ),
    ]
