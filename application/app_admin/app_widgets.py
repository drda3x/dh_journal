# -*- coding:utf-8 -*-

from django.forms.widgets import Widget, DateInput
from django.forms.fields import Field
from django.forms.utils import flatatt
from django.utils.html import format_html_join, format_html
from django.shortcuts import render_to_response
from django.template import loader


class ListWidget(Widget):

    def render(self, name, value, attrs=None):
        context = dict()
        context['attrs'] = flatatt(attrs)

        return loader.render_to_string('listWidget.html', context)
        #return format_html('<input {} />', flatatt(attrs)) + format_html_join('\n', '<li {}>{}</li>', ((flatatt(list_attrs), i) for i in xrange(10))) + '<script type="text/javascript">window.listWidget(\''+list_attrs['class']+'\')</script>'
        # html = super(ListWidget, self).render(name, value, attrs)
        # return html + format_html_join('\n', '<li>{}</li>', ([i] for i in xrange(10)))

    class Media:
        js = ('js/listWidget.js', )


class MyField(Field):
    pass
