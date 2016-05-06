from django import template

register = template.Library()

@register.filter
def is_type(value, type_name):
	return type(value).__name__ == type_name