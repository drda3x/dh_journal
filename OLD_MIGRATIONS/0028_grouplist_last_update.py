# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0027_auto_20160320_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouplist',
            name='last_update',
            field=models.DateField(default=datetime.datetime(2016, 1, 1, 0, 0), verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u043f\u0438\u0441\u0438', auto_now=True),
            preserve_default=False,
        ),
    ]
