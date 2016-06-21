from django import template

register = template.Library()


@register.filter
def joinby(val, sep):
	return sep.join(val)

@register.filter
def sum(arr, field_name):
	return reduce(lambda a, x: a + x[field_name] if isinstance(x, dict) else getattr(x, field_name), arr, 0)