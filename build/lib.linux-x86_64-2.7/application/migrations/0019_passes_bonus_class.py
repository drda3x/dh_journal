# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0018_bonusclasses__available_passes'),
    ]

    operations = [
        migrations.AddField(
            model_name='passes',
            name='bonus_class',
            field=models.ForeignKey(verbose_name='\u041c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441', blank=True, to='application.BonusClasses', null=True),
        ),
    ]
