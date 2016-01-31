# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0012_auto_20160131_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclasses',
            name='can_edit',
            field=models.BooleanField(default=True, verbose_name='\u041e\u0442\u043a\u0440\u044b\u0442 \u0434\u043b\u044f \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044f\u043c\u0438'),
        ),
    ]
