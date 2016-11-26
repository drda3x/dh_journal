# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampoPrises',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prise', models.PositiveIntegerField(verbose_name='\u0421\u0443\u043c\u043c\u0430')),
                ('date_from', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f')),
                ('date_to', models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f', blank=True)),
            ],
            options={
                'verbose_name': '\u0426\u0435\u043d\u044b \u043d\u0430 \u0441\u0430\u043c\u043f\u043e',
            },
        ),
        migrations.AlterUniqueTogether(
            name='sampoprises',
            unique_together=set([('date_from', 'date_to')]),
        ),
    ]
