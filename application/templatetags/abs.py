from django import template
register = template.Library()


@register.filter
def abs_filter(val):
    return abs(val)
