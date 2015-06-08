# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b')),
                ('start_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u0433\u0440\u0443\u043f\u043f\u044b')),
                ('days', models.CharField(max_length=30, verbose_name='\u0414\u043d\u0438 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f')),
                ('is_opened', models.BooleanField(default=True, verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430 \u043e\u0442\u043a\u0440\u044b\u0442\u0430')),
                ('teacher_follower', models.ForeignKey(related_name='follower', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044c - \u043f\u0430\u0440\u0442\u043d\u0435\u0440\u0448\u0430', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('teacher_leader', models.ForeignKey(related_name='leader', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044c - \u043f\u0430\u0440\u0442\u043d\u0435\u0440', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0413\u0440\u0443\u043f\u043f\u0443',
                'verbose_name_plural': '\u0413\u0440\u0443\u043f\u043f\u044b',
            },
        ),
        migrations.CreateModel(
            name='Passes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u0430')),
                ('lessons', models.PositiveIntegerField(verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043e\u0441\u0442\u0430\u0432\u0448\u0438\u0445\u0441\u044f \u0437\u0430\u043d\u044f\u0442\u0438\u0439')),
                ('skips', models.PositiveIntegerField(verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043e\u0441\u0442\u0430\u0432\u0448\u0438\u0445\u0441\u044f \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u043e\u0432')),
            ],
            options={
                'verbose_name': '\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442',
                'verbose_name_plural': '\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='PassTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('prise', models.PositiveIntegerField(verbose_name='\u0426\u0435\u043d\u0430')),
                ('lessons', models.PositiveIntegerField(verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0437\u0430\u043d\u044f\u0442\u0438\u0439')),
                ('skips', models.PositiveIntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u043e\u0432', blank=True)),
            ],
            options={
                'verbose_name': '\u0422\u0438\u043f \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u0430',
                'verbose_name_plural': '\u0422\u0438\u043f\u044b \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='\u0424\u0430\u043c\u0438\u043b\u0438\u044f')),
                ('last_name', models.CharField(max_length=30, verbose_name='\u0418\u043c\u044f')),
                ('father_name', models.CharField(max_length=30, null=True, verbose_name='\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e', blank=True)),
                ('phone', models.IntegerField(verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('e_mail', models.CharField(max_length=30, verbose_name='e-mail')),
            ],
            options={
                'verbose_name': '\u0423\u0447\u0435\u043d\u0438\u043a',
                'verbose_name_plural': '\u0423\u0447\u0435\u043d\u0438\u043a\u0438',
            },
        ),
        migrations.AddField(
            model_name='passes',
            name='pass_type',
            field=models.ForeignKey(verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442', to='application.PassTypes'),
        ),
        migrations.AddField(
            model_name='passes',
            name='student',
            field=models.ForeignKey(verbose_name='\u0423\u0447\u0435\u043d\u0438\u043a', to='application.Students'),
        ),
    ]
