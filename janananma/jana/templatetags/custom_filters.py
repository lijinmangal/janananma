from django import template
import calendar

register = template.Library()

@register.filter
def get_range(start, count):
    return range(start, start + count)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def get_month_name(month_number):
    try:
        return calendar.month_name[int(month_number)]
    except:
        return ""


