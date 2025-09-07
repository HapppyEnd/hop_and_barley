from urllib.parse import urlencode

from django import template
from django.db.models import Avg, QuerySet

register = template.Library()


@register.filter(name='range')
def template_range(stop: int, start: int = 0) -> range:
    """Create a range filter for templates.

    Args:
        stop: End value for range
        start: Start value for range (default: 0)

    Returns:
        Range object from start to stop
    """
    return range(start, stop)


@register.filter
def avg_rating(reviews: QuerySet) -> int:
    """Calculate average rating from reviews queryset.

    Args:
        reviews: QuerySet of review objects

    Returns:
        Rounded average rating or 0 if no reviews
    """
    if reviews:
        avg = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg or 0)
    return 0


@register.simple_tag(takes_context=True)
def modify_query(context: dict, **kwargs) -> str:
    """Modify query parameters in URL.

    Args:
        context: Template context containing request
        **kwargs: Query parameters to modify

    Returns:
        URL-encoded query string
    """
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
    """Get item from dictionary by key.

    Args:
        dictionary: Dictionary to get item from
        key: Key to look up

    Returns:
        Value from dictionary or None if not found
    """
    try:
        return dictionary.get(str(key))
    except (AttributeError, TypeError, KeyError):
        return None
