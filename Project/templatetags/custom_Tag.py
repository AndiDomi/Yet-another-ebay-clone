import decimal

from django import template

register = template.Library()

@register.filter(name = 'multiply')
def multiply(value, arg):
    andi = float(value)*float(arg)
    andi=float("%0.4f" % andi)
    return andi