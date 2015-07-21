# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_auto_20150721_2318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passes',
            name='group',
        ),
        migrations.AddField(
            model_name='passes',
            name='group',
            field=models.ForeignKey(verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', blank=True, to='application.Groups', null=True),
        ),
    ]
