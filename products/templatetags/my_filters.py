from urllib.parse import urlencode

from django import template
from django.db.models import Avg

register = template.Library()


@register.filter(name='range')
def template_range(stop, start=0):
    return range(start, stop)


@register.filter
def avg_rating(reviews):
    if reviews:
        avg = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg or 0)
    return 0


@register.simple_tag(takes_context=True)
def modify_query(context, **kwargs):
    request = context['request']
    params = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:
            if key in params:
                del params[key]
        else:
            params[key] = value

    return urlencode(params, doseq=True)


@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(str(key))
    except Exception:
        return None
