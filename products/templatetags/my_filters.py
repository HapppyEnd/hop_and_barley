from django import template

register = template.Library()

@register.filter(name='range')
def template_range(stop, start=0):
    return range(start, stop)

