# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0039_bonusclasses_within_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='external_available',
            field=models.BooleanField(default=False, verbose_name='\u041d\u0435 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043d\u0430 \u043b\u0435\u043d\u0434\u0438\u043d\u0433\u0435'),
        ),
    ]
