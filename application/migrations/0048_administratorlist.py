# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0047_auto_20170416_2316'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministratorList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('groups', models.ManyToManyField(to='application.Groups', null=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u043f\u043e\u0441\u0435\u0449\u0430\u0435\u043c\u044b\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
                ('student', models.ForeignKey(verbose_name='\u0423\u0447\u0435\u043d\u0438\u043a', to='application.Students')),
            ],
        ),
    ]
