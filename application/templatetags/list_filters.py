from django import template

register = template.Library()


@register.filter
def joinby(val, sep):
    return sep.join(val)


@register.filter
def in_list(val, _list):
    return val in map(int, _list.split())
