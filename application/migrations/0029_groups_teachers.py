# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_grouplist_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='teachers',
            field=models.ManyToManyField(related_name='teachers', null=True, verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0438', to='application.User', blank=True),
        ),
    ]
