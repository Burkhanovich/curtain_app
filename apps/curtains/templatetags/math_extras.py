from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Substract filter"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def multiply(value, arg):
    """Multiply filter"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def divide(value, arg):
    """Divide filter"""
    try:
        arg = int(arg)
        if arg == 0:
            return ''
        return int(value) / arg
    except (ValueError, TypeError):
        return ''

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        total = int(total)
        if total == 0:
            return 0
        return round((int(value) / total) * 100)
    except (ValueError, TypeError):
        return 0