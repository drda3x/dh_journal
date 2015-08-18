# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0020_passtypes_shown_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='passes',
            name='lessons_origin',
            field=models.PositiveIntegerField(default=8, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0438\u0437\u043d\u0430\u0447\u0430\u043b\u044c\u043d\u043e \u0437\u0430\u0434\u0430\u043d\u043d\u044b\u0445 \u0437\u0430\u043d\u044f\u0442\u0438\u0439'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='passes',
            name='skips_origin',
            field=models.PositiveIntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0438\u0437\u043d\u0430\u0447\u0430\u043b\u044c\u043d\u043e \u0437\u0430\u0434\u0430\u043d\u043d\u044b\u0445 \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u043e\u0432', blank=True),
        ),
    ]
