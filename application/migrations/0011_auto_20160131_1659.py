# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0010_auto_20160118_1933'),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430')),
                ('time', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f', blank=True)),
                ('hall', models.ForeignKey(verbose_name='\u0417\u0430\u043b', to='application.DanceHalls')),
                ('teacher_follower', models.ForeignKey(related_name='teacher2', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044c 2', blank=True, to='application.User', null=True)),
                ('teacher_leader', models.ForeignKey(related_name='teacher1', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044c 1', blank=True, to='application.User', null=True)),
            ],
            options={
                'verbose_name': '\u041c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441',
                'verbose_name_plural': '\u041c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441\u044b',
            },
        ),
        migrations.AlterModelOptions(
            name='sampoprises',
            options={'verbose_name': '\u0426\u0435\u043d\u044b \u043d\u0430 \u0441\u0430\u043c\u043f\u043e', 'verbose_name_plural': '\u0426\u0435\u043d\u044b \u043d\u0430 \u0441\u0430\u043c\u043f\u043e'},
        ),
        migrations.AlterUniqueTogether(
            name='bonusclasses',
            unique_together=set([('date', 'hall')]),
        ),
    ]
