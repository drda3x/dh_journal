# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_passes_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passes',
            name='pass_type',
            field=models.ForeignKey(default=None, blank=True, to='application.PassTypes', null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442'),
        ),
    ]
