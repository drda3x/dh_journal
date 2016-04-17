# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0031_auto_20160417_1635'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groups',
            old_name='available_passes_new',
            new_name='available_passes',
        ),
        migrations.RenameField(
            model_name='groups',
            old_name='external_passes_new',
            new_name='external_passes',
        ),
        migrations.RemoveField(
            model_name='groups',
            name='_available_passes',
        ),
        migrations.RemoveField(
            model_name='groups',
            name='_external_passes',
        ),
    ]
