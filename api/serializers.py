from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from phonenumber_field.serializerfields import PhoneNumberField
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

    def to_representation(self, instance):
        """Add nested parent data."""
        data = super().to_representation(instance)
        if instance.parent:
            data['parent'] = {
                'id': instance.parent.id,
                'name': instance.parent.name,
                'slug': instance.parent.slug
            }
        return data


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'category', 'category_id',
            'price', 'image', 'get_image_url', 'is_active', 'stock'
        )
        read_only_fields = ('id', 'slug', 'get_image_url')

    def create(self, validated_data):
        """Create product with category_id."""
        category_id = validated_data.pop('category_id')
        validated_data['category_id'] = category_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update product with category_id."""
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            validated_data['category_id'] = category_id
        return super().update(instance, validated_data)


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
    phone = extend_schema_field(serializers.CharField(
        help_text="Phone number in international format (e.g., +1234567890)"
    ))(PhoneNumberField(required=False, allow_null=True))

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
    phone = extend_schema_field(serializers.CharField(
        help_text="Phone number in international format (e.g., +1234567890)"
    ))(PhoneNumberField(required=False, allow_null=True))

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


class CartItemSerializer(serializers.Serializer):
    """Serializer for session-based cart items."""
    product_id = serializers.IntegerField(read_only=True)
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    stock = serializers.IntegerField(read_only=True)


class CartSerializer(serializers.Serializer):
    """Serializer for session-based cart."""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        """Get total cart price from session cart."""
        cart = obj.get('cart_instance')
        if cart:
            return cart.get_total_price()
        return "$0.00"

    def get_items_count(self, obj):
        """Get total number of items in cart."""
        cart = obj.get('cart_instance')
        if cart:
            return len(cart)
        return 0
