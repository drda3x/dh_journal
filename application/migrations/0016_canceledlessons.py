# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0015_auto_20150803_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanceledLessons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0442\u043c\u0435\u043d\u0435\u043d\u043d\u043e\u0433\u043e \u0443\u0440\u043e\u043a\u0430')),
                ('group', models.ForeignKey(to='application.Groups')),
            ],
            options={
                'verbose_name': '\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043d\u043e\u0435 \u0437\u0430\u043d\u044f\u0442\u0438\u0435',
                'verbose_name_plural': '\u041e\u0442\u043c\u0435\u043d\u0435\u043d\u043d\u044b\u0435 \u0437\u0430\u043d\u044f\u0442\u0438\u044f',
            },
        ),
    ]
