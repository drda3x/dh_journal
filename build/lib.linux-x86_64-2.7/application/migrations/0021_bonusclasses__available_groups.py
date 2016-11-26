# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0020_auto_20160229_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclasses',
            name='_available_groups',
            field=models.CommaSeparatedIntegerField(max_length=1000, null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b', blank=True),
        ),
    ]
