# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0040_groups_external_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='passtypes',
            name='is_actual',
            field=models.BooleanField(default=True, verbose_name='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u043c\u044b\u0439'),
        ),
    ]
