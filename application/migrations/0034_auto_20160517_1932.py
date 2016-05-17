# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0033_groups_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='about',
            field=models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.FileField(null=True, upload_to=b'/home/da3x/freelance/teacher_book/application/static/img', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='video',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
