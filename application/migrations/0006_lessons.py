# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_auto_20150610_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lessons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043d\u044f\u0442\u0438\u044f')),
                ('presence_sign', models.BooleanField(default=False, verbose_name='\u041e\u0442\u043c\u0435\u0442\u043a\u0430 \u043e \u043f\u0440\u0438\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0438')),
                ('group', models.ForeignKey(verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', to='application.Groups')),
                ('group_pass', models.ForeignKey(related_name='lesson_group_pass', verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442', to='application.Passes')),
                ('student', models.ForeignKey(verbose_name='\u0423\u0447\u0435\u043d\u0438\u0435', to='application.Students')),
            ],
            options={
                'verbose_name': '\u0416\u0443\u0440\u043d\u0430\u043b \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u044f',
            },
        ),
    ]
