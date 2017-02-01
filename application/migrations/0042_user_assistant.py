# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0041_passtypes_is_actual'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='assistant',
            field=models.BooleanField(default=False, verbose_name='\u0410\u0441\u0441\u0438\u0441\u0442\u0435\u043d\u0442'),
        ),
    ]
