# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0048_telegramchats'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramchats',
            name='is_authorised',
            field=models.BooleanField(default=False, verbose_name='\u0410\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d'),
        ),
    ]
