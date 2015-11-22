# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_auto_20151121_1230'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampoPasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name='\u0418\u043c\u044f')),
                ('surname', models.TextField(verbose_name='\u0444\u0430\u043c\u0438\u043b\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0421\u0410\u041c\u041f\u041e',
            },
        ),
        migrations.CreateModel(
            name='SampoPayments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043f\u043b\u0430\u0442\u044b')),
                ('people_count', models.PositiveIntegerField(verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043b\u044e\u0434\u0435\u0439')),
                ('money', models.PositiveIntegerField(verbose_name='\u0421\u0443\u043c\u043c\u0430')),
                ('staff', models.ForeignKey(verbose_name='\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u0421\u0410\u041c\u041f\u041e', to='application.User')),
            ],
            options={
                'verbose_name': '\u041e\u043f\u043b\u0430\u0442\u0430 \u0441\u0430\u043c\u043f\u043e',
            },
        ),
        migrations.AddField(
            model_name='sampopasses',
            name='payment',
            field=models.ForeignKey(verbose_name='\u041e\u043f\u043b\u0430\u0442\u0430 \u0430\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u0430', to='application.SampoPayments'),
        ),
    ]
