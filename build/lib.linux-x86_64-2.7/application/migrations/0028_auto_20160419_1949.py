# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0027_auto_20160320_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='debts',
            options={'verbose_name': '\u0414\u043e\u043b\u0433', 'verbose_name_plural': '\u0414\u043e\u043b\u0433\u0438'},
        ),
        migrations.RemoveField(
            model_name='groups',
            name='_available_passes',
        ),
        migrations.AddField(
            model_name='grouplist',
            name='last_update',
            field=models.DateField(default=datetime.datetime(2016, 1, 1, 0, 0), verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435 \u0437\u0430\u043f\u0438\u0441\u0438', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='groups',
            name='available_passes',
            field=models.ManyToManyField(related_name='avp', null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0435\u0439', to='application.PassTypes', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='external_passes',
            field=models.ManyToManyField(related_name='exp', null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u043d\u0430 \u0432\u043d\u0435\u0448\u043d\u0438\u0445 \u0441\u0430\u0439\u0442\u0430\u0445', to='application.PassTypes', blank=True),
        ),
        migrations.AddField(
            model_name='groups',
            name='teachers',
            field=models.ManyToManyField(related_name='allteachers', null=True, verbose_name='\u041f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0438', to='application.User', blank=True),
        ),
    ]
