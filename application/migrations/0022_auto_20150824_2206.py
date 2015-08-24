# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0021_auto_20150818_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debts',
            name='val',
            field=models.FloatField(verbose_name='\u0421\u0443\u043c\u043c\u0430'),
        ),
    ]
