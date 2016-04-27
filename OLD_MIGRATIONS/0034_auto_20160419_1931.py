# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0033_auto_20160417_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='teachers',
            field=models.ManyToManyField(related_name='allteachers', null=True, verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0438', to='application.User', blank=True),
        ),
    ]
