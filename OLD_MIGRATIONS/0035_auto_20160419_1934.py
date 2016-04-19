# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0034_auto_20160419_1931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groups',
            name='teacher_follower',
        ),
        migrations.RemoveField(
            model_name='groups',
            name='teacher_leader',
        ),
    ]
