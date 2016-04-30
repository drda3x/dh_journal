from django import template

register = template.Library()


@register.filter
def joinby(val, sep):
	return sep.join(val)