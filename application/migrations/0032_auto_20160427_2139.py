# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0031_bonusclasses_teachers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonusclasses',
            name='available_groups',
            field=models.ManyToManyField(to='application.Groups', null=True, verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True),
        ),
        migrations.AlterField(
            model_name='bonusclasses',
            name='available_passes',
            field=models.ManyToManyField(to='application.PassTypes', null=True, verbose_name='\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b', blank=True),
        ),
    ]
