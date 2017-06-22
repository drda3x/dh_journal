# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0047_auto_20170416_2316'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeleGramChats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chat_id', models.PositiveIntegerField(verbose_name='ID \u0447\u0430\u0442\u0430')),
            ],
        ),
    ]
