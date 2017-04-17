# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0044_auto_20170416_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='admincalls',
            name='related_call',
            field=models.ForeignKey(blank=True, to='application.AdminCalls', null=True),
        ),
    ]
