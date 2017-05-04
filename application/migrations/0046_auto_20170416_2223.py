# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0045_admincalls_related_call'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admincalls',
            name='message',
            field=models.TextField(max_length=300, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435', blank=True),
        ),
    ]
