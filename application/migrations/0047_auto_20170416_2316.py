# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0046_auto_20170416_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admincalls',
            name='message',
            field=models.ForeignKey(verbose_name='\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True, to='application.Comments', null=True),
        ),
    ]
