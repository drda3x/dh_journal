# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0014_bonusclasslist_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bonusclasslist',
            old_name='bonus_class',
            new_name='group',
        ),
        migrations.AlterUniqueTogether(
            name='bonusclasslist',
            unique_together=set([('group', 'student')]),
        ),
    ]
