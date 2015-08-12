# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0019_grouplist_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='passtypes',
            name='shown_value',
            field=models.CharField(max_length=30, null=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u043c\u043e\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435(\u0435\u0441\u043b\u0438 \u043f\u0443\u0441\u0442\u043e\u0435 - \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0446\u0435\u043d\u0430 \u0437\u0430 \u0437\u0430\u043d\u044f\u0442\u0438\u0435)', blank=True),
        ),
    ]
