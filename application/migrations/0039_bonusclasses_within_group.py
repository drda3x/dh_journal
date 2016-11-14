# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0038_auto_20160703_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclasses',
            name='within_group',
            field=models.ForeignKey(related_name='whthin_group', verbose_name='\u041c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441 \u0432 \u0440\u0430\u043c\u043a\u0430\u0445 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True, to='application.Groups', null=True),
        ),
    ]
