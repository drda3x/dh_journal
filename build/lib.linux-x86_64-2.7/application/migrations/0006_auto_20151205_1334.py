# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_sampopassusage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sampopayments',
            name='money',
            field=models.IntegerField(verbose_name='\u0421\u0443\u043c\u043c\u0430'),
        ),
    ]
