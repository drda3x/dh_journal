# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0037_auto_20160523_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dancehalls',
            name='map',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='photo1',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='photo2',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='dancehalls',
            name='photo3',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='_days',
            field=models.CommaSeparatedIntegerField(max_length=13, verbose_name='\u0414\u043d\u0438'),
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.FileField(upload_to=b'', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True),
        ),
    ]
