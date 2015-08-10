# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0017_passtypes_sequence'),
    ]

    operations = [
        migrations.CreateModel(
            name='Debts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430')),
                ('val', models.PositiveIntegerField(verbose_name='\u0421\u0443\u043c\u043c\u0430')),
                ('group', models.ForeignKey(to='application.Groups')),
                ('student', models.ForeignKey(to='application.Students')),
            ],
        ),
        migrations.AlterField(
            model_name='passtypes',
            name='sequence',
            field=models.PositiveIntegerField(null=True, verbose_name='\u041f\u043e\u0440\u044f\u0434\u043a\u043e\u0432\u044b\u0439 \u043d\u043e\u043c\u0435\u0440', blank=True),
        ),
    ]
