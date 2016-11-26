# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0016_auto_20160223_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passes',
            name='start_date',
            field=models.DateField(null=True, verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u0430', blank=True),
        ),
    ]
