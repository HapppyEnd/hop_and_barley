from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from api.setializers import ProductSerializer
from products.models import Product


class ProductViewSet(ModelViewSet):
    """API viewset for products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('name',)
    filterset_fields = ('created_at', 'reviews__rating', 'price')
