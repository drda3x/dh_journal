# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0010_students_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='passes',
            name='frozen_date',
            field=models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0437\u0430\u043c\u043e\u0440\u043e\u0437\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='lessons',
            name='status',
            field=models.IntegerField(default=0, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u0437\u0430\u043d\u044f\u0442\u0438\u044f', choices=[(2, b'not_attended'), (1, b'attended'), (3, b'frozen'), (5, b'written_off'), (4, b'moved'), (0, b'not_processed')]),
        ),
    ]
