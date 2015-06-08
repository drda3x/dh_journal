# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=2)),
            ],
        ),
        migrations.RemoveField(
            model_name='groups',
            name='days',
        ),
        migrations.AlterField(
            model_name='groups',
            name='teacher_follower',
            field=models.ForeignKey(related_name='follower', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434 2', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='teacher_leader',
            field=models.ForeignKey(related_name='leader', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434 1', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='days',
            field=models.ManyToManyField(to='application.Days', verbose_name='\u0414\u043d\u0438 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f'),
        ),
    ]
