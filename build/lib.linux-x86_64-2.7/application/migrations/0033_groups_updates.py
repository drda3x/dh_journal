# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0032_auto_20160427_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='updates',
            field=models.CommaSeparatedIntegerField(max_length=200, null=True, verbose_name='\u0414\u043e\u043d\u0430\u0431\u043e\u0440\u044b \u0432 \u0433\u0440\u0443\u043f\u043f\u0443', blank=True),
        ),
    ]
