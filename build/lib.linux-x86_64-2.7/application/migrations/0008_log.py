# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_sampopayments_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0438\u0441\u0438')),
                ('msg', models.TextField(max_length=1000, verbose_name='\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435')),
            ],
        ),
    ]
