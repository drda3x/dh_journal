# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0022_auto_20150824_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='passes',
            name='opener',
            field=models.ForeignKey(blank=True, to='application.User', null=True),
        ),
    ]
