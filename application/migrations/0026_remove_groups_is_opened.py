# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_auto_20160314_2124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groups',
            name='is_opened',
        ),
    ]
