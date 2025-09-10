from urllib.parse import urlencode

from django import template
from django.db.models import Avg, QuerySet

register = template.Library()


@register.filter(name='range')
def template_range(value: int, start: int = 0) -> range:
    """Create a range filter for templates."""
    return range(start, value)


@register.filter
def avg_rating(reviews: QuerySet) -> int:
    """Calculate average rating from reviews queryset."""
    if reviews:
        avg = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg or 0)
    return 0


@register.simple_tag(takes_context=True)
def modify_query(context: dict, **kwargs) -> str:
    """Modify query parameters in URL."""
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
def get_item(dictionary: dict, key: str) -> any:
    """Get item from dictionary by key."""
    try:
        return dictionary.get(str(key))
    except (AttributeError, TypeError, KeyError):
        return None
