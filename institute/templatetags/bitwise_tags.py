from django import template 
from institute.views import TimeHistory

register = template.Library()

@register.filter
def bitwise_and(value, arg):
    return bool(value & arg)

@register.filter
def bitwise_or(value, arg):
    return bool(value | arg)

@register.filter
def masking(value):
    return value[:1] + '**'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_constants(name):
    return getattr(TimeHistory, name, None)

@register.filter
def isPassenger(value):
    return bool(value & TimeHistory.BILLING_PASSENGER)

@register.filter
def isOverPeople(value):
    return bool(value & TimeHistory.BILLING_OVERPEOPLE)

@register.filter
def isOverTime(value):
    return bool(value & TimeHistory.BILLING_OVERTIME)

@register.filter
def contained(item, itemlist):
    for i in itemlist:
        if item == i.id:
            return True

    return False
