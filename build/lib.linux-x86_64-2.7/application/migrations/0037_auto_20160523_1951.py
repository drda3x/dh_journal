# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0036_auto_20160517_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouplevels',
            name='course_details',
            field=models.TextField(null=True, verbose_name='\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0438 \u043e \u043a\u0443\u0440\u0441\u0435', blank=True),
        ),
        migrations.AddField(
            model_name='grouplevels',
            name='course_results',
            field=models.TextField(null=True, verbose_name='\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b \u043f\u0440\u043e\u0445\u043e\u0436\u0434\u0435\u043d\u0438\u044f \u043a\u0443\u0440\u0441\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='course_details',
            field=models.TextField(null=True, verbose_name='\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0438 \u043e \u0433\u0440\u0443\u043f\u043f\u0435', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='course_results',
            field=models.TextField(null=True, verbose_name='\u041d\u0430\u0432\u044b\u043a \u043f\u043e\u0441\u043b\u0435 \u043f\u0440\u043e\u0445\u043e\u0436\u0434\u0435\u043d\u0438\u044f', blank=True),
        ),
    ]
