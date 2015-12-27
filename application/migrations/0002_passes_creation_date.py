# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passes',
            name='creation_date',
            field=models.DateField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0434\u0430\u043d\u0438\u044f(\u043e\u043f\u043b\u0430\u0442\u044b \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u0430)', null=True),
        ),
    ]
