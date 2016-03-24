# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0026_remove_groups_is_opened'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouplevels',
            name='name',
            field=models.CharField(max_length=50, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='grouplevels',
            name='string_code',
            field=models.CharField(max_length=50, verbose_name='\u041a\u043e\u0434'),
        ),
    ]
