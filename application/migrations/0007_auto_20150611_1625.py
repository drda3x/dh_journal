# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_lessons'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', to='application.Groups')),
                ('student', models.ForeignKey(verbose_name='\u0423\u0447\u0435\u043d\u0438\u043a', to='application.Students')),
            ],
            options={
                'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0433\u0440\u0443\u043f\u043f\u044b',
                'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043a\u0438 \u0433\u0440\u0443\u043f\u043f',
            },
        ),
        migrations.RemoveField(
            model_name='passes',
            name='group',
        ),
        migrations.AddField(
            model_name='passes',
            name='group',
            field=models.ManyToManyField(to='application.Groups', null=True, verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', blank=True),
        ),
    ]
