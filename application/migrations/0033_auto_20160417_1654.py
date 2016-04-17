# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0032_auto_20160417_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='available_passes',
            field=models.ManyToManyField(related_name='avp', null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0435\u0439', to='application.PassTypes', blank=True),
        ),
        migrations.AlterField(
            model_name='groups',
            name='external_passes',
            field=models.ManyToManyField(related_name='exp', null=True, verbose_name='\u0410\u0431\u043e\u043d\u0435\u043c\u0435\u043d\u0442\u044b \u0434\u043b\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u043d\u0430 \u0432\u043d\u0435\u0448\u043d\u0438\u0445 \u0441\u0430\u0439\u0442\u0430\u0445', to='application.PassTypes', blank=True),
        ),
    ]
