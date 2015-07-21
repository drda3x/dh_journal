# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_auto_20150721_2258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passtypes',
            old_name='multi_pass',
            new_name='one_group_pass',
        ),
    ]
