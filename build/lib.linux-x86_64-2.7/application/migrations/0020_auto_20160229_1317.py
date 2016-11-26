# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0019_passes_bonus_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='bonus_class',
            field=models.ForeignKey(blank=True, to='application.BonusClasses', null=True),
        ),
        migrations.AlterField(
            model_name='comments',
            name='group',
            field=models.ForeignKey(blank=True, to='application.Groups', null=True),
        ),
    ]
