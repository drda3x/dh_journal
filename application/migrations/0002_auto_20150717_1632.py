# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessons',
            name='presence_sign',
        ),
        migrations.AddField(
            model_name='lessons',
            name='status',
            field=models.IntegerField(default=0, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u0437\u0430\u043d\u044f\u0442\u0438\u044f', choices=[(3, b'frozen'), (2, b'not_attended'), (1, b'attended'), (4, b'moved'), (0, b'not_processed')]),
        ),
        migrations.AddField(
            model_name='passtypes',
            name='multi_pass',
            field=models.BooleanField(default=True, verbose_name='\u041e\u0434\u043d\u0430 \u0433\u0440\u0443\u043f\u043f\u0430'),
        ),
    ]
