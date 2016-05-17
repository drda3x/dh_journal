# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0034_auto_20160517_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='duration',
            field=models.IntegerField(null=True, verbose_name='\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u043a\u0443\u0440\u0441\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='free_placees',
            field=models.IntegerField(null=True, verbose_name='\u041e\u0431\u0449\u0435\u0435 \u043a\u043e\u043b-\u0432\u043e \u043c\u0435\u0441\u0442 \u0432 \u0433\u0440\u0443\u043f\u043f\u0435', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='lending_message',
            field=models.CharField(max_length=100, null=True, verbose_name='\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0432 \u0448\u0430\u043f\u043a\u0435 \u043b\u0435\u043d\u0434\u0438\u043d\u0433\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.FileField(upload_to=b'/home/da3x/freelance/teacher_book/application/static/img', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='video',
            field=models.CharField(max_length=100, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e', blank=True),
        ),
    ]
