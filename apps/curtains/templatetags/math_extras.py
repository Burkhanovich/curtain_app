from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Substract filter"""
    return int(value) - int(arg)

@register.filter
def multiply(value, arg):
    """Multiply filter"""
    return int(value) * int(arg)

@register.filter
def divide(value, arg):
    """Divide filter"""
    return int(value) / int(arg)

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((int(value) / int(total)) * 100)