# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0051_auto_20180131_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='sampopassusage',
            name='hall',
            field=models.ForeignKey(default=4, verbose_name='\u0417\u0430\u043b', to='application.DanceHalls'),
        ),
        migrations.AddField(
            model_name='sampopayments',
            name='hall',
            field=models.ForeignKey(default=4, verbose_name='\u0417\u0430\u043b', to='application.DanceHalls'),
        ),
    ]
