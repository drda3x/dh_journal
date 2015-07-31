# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0013_auto_20150729_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('add_date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('text', models.TextField(max_length=100, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u044f')),
                ('group', models.ForeignKey(to='application.Groups')),
                ('student', models.ForeignKey(to='application.Students')),
            ],
            options={
                'verbose_name': '\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439',
                'verbose_name_plural': '\u041a\u043e\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438',
            },
        ),
        migrations.AlterModelOptions(
            name='dancehalls',
            options={'verbose_name': '\u0417\u0430\u043b', 'verbose_name_plural': '\u0417\u0430\u043b\u044b'},
        ),
    ]
