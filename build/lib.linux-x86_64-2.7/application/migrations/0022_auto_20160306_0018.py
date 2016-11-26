# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0021_bonusclasses__available_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dances',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0442\u0430\u043d\u0435\u0446',
                'verbose_name_plural': '\u0422\u0430\u043d\u0446\u044b',
            },
        ),
        migrations.CreateModel(
            name='GroupLevels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
                ('string_code', models.CharField(max_length=50, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xb4')),
            ],
            options={
                'verbose_name': '\u0423\u0440\u043e\u0432\u0435\u043d\u044c \u0433\u0440\u0443\u043f\u043f\u044b',
                'verbose_name_plural': '\u0423\u0440\u043e\u0432\u043d\u0438 \u0433\u0440\u0443\u043f\u043f',
            },
        ),
        migrations.AddField(
            model_name='dancehalls',
            name='address',
            field=models.CharField(max_length=200, null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441', blank=True),
        ),
        migrations.AddField(
            model_name='dancehalls',
            name='time_to_come',
            field=models.PositiveIntegerField(null=True, verbose_name='\u041c\u0438\u043d\u0443\u0442\u044b \u043e\u0442 \u043c\u0435\u0442\u0440\u043e', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='dance',
            field=models.ForeignKey(blank=True, to='application.Dances', null=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='level',
            field=models.ForeignKey(blank=True, to='application.GroupLevels', null=True),
        ),
    ]
