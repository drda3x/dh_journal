# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0013_bonusclasses_can_edit'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonusclasslist',
            name='active',
            field=models.BooleanField(default=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u0430\u043a\u0442\u0438\u0432\u043d\u0430'),
        ),
    ]
