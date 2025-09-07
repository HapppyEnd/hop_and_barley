from rest_framework.serializers import ModelSerializer

from products.models import Product


class ProductSerializer(ModelSerializer):
    """Serializer for Product model.

    Provides serialization and deserialization for Product instances.
    Includes basic product information for API responses.
    """
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'price', 'image')
