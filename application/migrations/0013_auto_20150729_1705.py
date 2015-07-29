# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0012_auto_20150729_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='DanceHalls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('station', models.CharField(max_length=50, verbose_name='\u0421\u0442\u0430\u043d\u0446\u0438\u044f \u043c\u0435\u0442\u0440\u043e')),
                ('prise', models.PositiveIntegerField(verbose_name='\u0426\u0435\u043d\u0430')),
            ],
        ),
        migrations.AddField(
            model_name='groups',
            name='dance_hall',
            field=models.ForeignKey(default=None, verbose_name='\u0417\u0430\u043b', to='application.DanceHalls'),
            preserve_default=False,
        ),
    ]
