# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0043_auto_20170130_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminCalls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0432\u043e\u043d\u043a\u0430')),
                ('responce_type', models.CharField(max_length=150, verbose_name='\u0422\u0438\u043f \u043e\u0442\u0432\u0435\u0442\u0430')),
                ('message', models.CharField(max_length=300, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435', blank=True)),
                ('is_solved', models.BooleanField(default=False, verbose_name='\u0424\u043b\u0430\u0433 \u043e \u0440\u0435\u0448\u0435\u043d\u0438\u0438 \u0432\u043e\u043f\u0440\u043e\u0441\u0430')),
                ('caller', models.ForeignKey(verbose_name='\u0417\u0432\u043e\u043d\u0438\u0432\u0448\u0438\u0439', to='application.User')),
                ('group', models.ForeignKey(verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', to='application.Groups')),
                ('group_pass', models.ForeignKey(verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442', blank=True, to='application.Passes', null=True)),
                ('student', models.ForeignKey(verbose_name='\u0423\u0447\u0435\u043d\u0438\u043a', to='application.Students')),
            ],
        ),
        migrations.AlterField(
            model_name='teacherssubstitution',
            name='teachers',
            field=models.ManyToManyField(to='application.User', null=True, verbose_name='\u0421\u043e\u0441\u0442\u0430\u0432 \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0435\u0439', blank=True),
        ),
    ]
