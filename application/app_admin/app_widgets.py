# -*- coding:utf-8 -*-

from datetime import datetime
from time import mktime
from django.forms.widgets import Widget, DateInput
from django.forms.fields import Field
from django.forms.utils import flatatt
from django.utils.html import format_html_join, format_html
from django.shortcuts import render_to_response
from django.template import loader


DATE_FORMAT = '%d.%m.%Y'


class ListWidget(Widget):

    def render(self, name, value, attrs=None):
        context = dict()
        attrs['name'] = name
        context['attrs'] = flatatt(attrs)
        context['values'] = map(lambda val: datetime.fromtimestamp(int(val)).strftime(DATE_FORMAT), value.split(',')) if value else []

        return loader.render_to_string('listWidget.html', context)

    class Media:
        js = ('js/listWidget.js', )


class MyField(Field):

    def str_to_dates(self, _str):
        for dt in _str.split(';'):
            if not dt:
                continue

            yield int(mktime(datetime.strptime(dt, DATE_FORMAT).timetuple()))

    def to_python(self, value):
        return ','.join(map(str, self.str_to_dates(value)))
