# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0011_auto_20160131_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusClassList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attendance', models.BooleanField(default=False, verbose_name='\u041f\u0440\u0438\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0435')),
                ('bonus_class', models.ForeignKey(to='application.BonusClasses')),
                ('group_pass', models.ForeignKey(blank=True, to='application.Passes', null=True)),
                ('student', models.ForeignKey(to='application.Students')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bonusclasslist',
            unique_together=set([('bonus_class', 'student')]),
        ),
    ]
