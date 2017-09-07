# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0048_administratorlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='administratorlist',
            name='status',
            field=models.CharField(default=b'a', max_length=20, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'a', b'active'), (b'd2', b'complete_deted'), (b'd1', b'simple_deleted')]),
        ),
    ]
