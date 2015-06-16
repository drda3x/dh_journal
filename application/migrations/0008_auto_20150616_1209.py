# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_auto_20150611_1625'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='grouplist',
            unique_together=set([('group', 'student')]),
        ),
    ]
