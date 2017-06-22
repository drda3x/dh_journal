# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0049_telegramchats_is_authorised'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramchats',
            name='last_message_update',
            field=models.PositiveIntegerField(default=0, verbose_name='ID \u0447\u0430\u0442\u0430'),
        ),
    ]
