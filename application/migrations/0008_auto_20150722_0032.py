# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_auto_20150721_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passes',
            name='skips',
            field=models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043e\u0441\u0442\u0430\u0432\u0448\u0438\u0445\u0441\u044f \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u043e\u0432'),
        ),
    ]
