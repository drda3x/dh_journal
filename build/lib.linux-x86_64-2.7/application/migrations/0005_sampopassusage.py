# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20151122_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampoPassUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f')),
                ('sampo_pass', models.ForeignKey(verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442', to='application.SampoPasses')),
            ],
            options={
                'verbose_name': '\u041e\u0442\u043c\u0435\u0442\u043a\u0438 \u043e \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0438 \u0441\u0430\u043c\u043f\u043e',
            },
        ),
    ]
