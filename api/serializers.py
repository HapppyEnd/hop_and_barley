from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from orders.models import Order, OrderItem
from products.models import Category, Product, Review

user_model = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that uses email instead of username."""

    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        if 'username' in self.fields:
            del self.fields['username']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent')
        read_only_fields = ('id', 'slug')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'category',
            'price', 'image', 'get_image_url', 'is_active', 'stock'
        )
        read_only_fields = ('id', 'slug', 'get_image_url')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""

    class Meta:
        model = Review
        fields = (
            'id', 'product', 'user', 'rating', 'title', 'comment', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total')
        read_only_fields = ('id', 'price', 'total')


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'status', 'get_status_display', 'shipping_address',
            'total_price', 'items', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        """Create order with items."""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = user_model
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'city', 'address'
        )
        read_only_fields = ('id', 'full_name')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password fields."""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = user_model
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'city', 'address', 'password',
            'password_confirm'
        )
        read_only_fields = ('id', 'full_name')

    def validate(self, data):
        """Validate password confirmation."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return data
