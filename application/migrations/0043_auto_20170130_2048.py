# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0042_user_assistant'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeachersSubstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043c\u0435\u043d\u044b')),
                ('group', models.ForeignKey(db_constraint=False, verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430', to='application.Groups')),
                ('teachers', models.ManyToManyField(to='application.User', verbose_name='\u0421\u043e\u0441\u0442\u0430\u0432 \u043f\u0440\u0435\u043f\u043e\u0434\u0430\u0432\u0430\u0442\u0435\u043b\u0435\u0439')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='teacherssubstitution',
            unique_together=set([('date', 'group')]),
        ),
    ]
