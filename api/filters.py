import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter for Product model."""

    category = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte'
    )
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'is_active']
