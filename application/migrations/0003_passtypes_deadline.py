# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_auto_20150717_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='passtypes',
            name='deadline',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f'),
        ),
    ]
