# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('application', '0011_auto_20150728_1707'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.AlterField(
            model_name='groups',
            name='teacher_follower',
            field=models.ForeignKey(related_name='follower', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434 2', blank=True, to='application.User', null=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='teacher_leader',
            field=models.ForeignKey(related_name='leader', verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434 1', blank=True, to='application.User', null=True),
        ),
    ]
