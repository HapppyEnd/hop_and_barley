from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.filters import ProductFilter
from api.permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from api.serializers import (CartSerializer, CategorySerializer,
                             OrderSerializer, ProductSerializer,
                             ReviewSerializer, UserRegistrationSerializer,
                             UserSerializer)
from orders.cart import Cart as SessionCart
from orders.models import Order
from products.models import Category, Product, Review

user_model = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List Categories",
        description="Get list of all product categories",
        tags=["Categories"]
    ),
    create=extend_schema(
        summary="Create Category",
        description="Create new category (admin only)",
        tags=["Categories"]
    ),
    retrieve=extend_schema(
        summary="Category Details",
        description="Get specific category information",
        tags=["Categories"]
    ),
    update=extend_schema(
        summary="Update Category",
        description="Update category (admin only)",
        tags=["Categories"]
    ),
    partial_update=extend_schema(
        summary="Partial Update Category",
        description="Partially update category (admin only)",
        operation_id="update_category_partial",
        tags=["Categories"]
    ),
    destroy=extend_schema(
        summary="Delete Category",
        description="Delete category (admin only)",
        tags=["Categories"]
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    )
    search_fields = ('name',)
    ordering_fields = ('name', 'created_at')
    ordering = ('name',)


@extend_schema_view(
    list=extend_schema(
        summary="List Products",
        description="Get list of products with filtering and search",
        tags=["Products"]
    ),
    create=extend_schema(
        summary="Create Product",
        description="Create new product (admin only)",
        tags=["Products"]
    ),
    retrieve=extend_schema(
        summary="Product Details",
        description="Get specific product information",
        tags=["Products"]
    ),
    update=extend_schema(
        summary="Update Product",
        description="Update product (admin only)",
        tags=["Products"]
    ),
    partial_update=extend_schema(
        summary="Partial Update Product",
        description="Partially update product (admin only)",
        tags=["Products"]
    ),
    destroy=extend_schema(
        summary="Delete Product",
        description="Delete product (admin only)",
        tags=["Products"]
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products with filtering and search."""

    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    )
    filterset_class = ProductFilter
    search_fields = ('name', 'description')
    ordering_fields = ('price', 'created_at', 'name')
    ordering = ('-created_at',)

    def get_queryset(self):
        """Filter products by active status for non-admin users."""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


@extend_schema_view(
    list=extend_schema(
        summary="List Reviews",
        description="Get list of reviews (requires authentication)",
        tags=["Reviews"]
    ),
    create=extend_schema(
        summary="Create Review",
        description="Create new review (only for purchasers)",
        tags=["Reviews"]
    ),
    retrieve=extend_schema(
        summary="Review Details",
        description="Get specific review information",
        tags=["Reviews"]
    ),
    update=extend_schema(
        summary="Update Review",
        description="Update your review",
        tags=["Reviews"]
    ),
    partial_update=extend_schema(
        summary="Partial Update Review",
        description="Partially update your review",
        tags=["Reviews"]
    ),
    destroy=extend_schema(
        summary="Delete Review",
        description="Delete your review",
        tags=["Reviews"]
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product reviews."""

    queryset = Review.objects.all().select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('created_at', 'rating')
    ordering = ('-created_at',)

    def perform_create(self, serializer):
        """Set the user when creating a review."""
        product = serializer.validated_data['product']
        user = self.request.user

        if Review.objects.filter(user=user, product=product).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'product': 'You have already reviewed this product.'
            })

        if not product.user_can_review(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only review products you have purchased and received."
            )

        serializer.save(user=user)


@extend_schema_view(
    list=extend_schema(
        summary="List Orders",
        description="Get list of orders (requires authentication)",
        tags=["Orders"]
    ),
    create=extend_schema(
        summary="Create Order",
        description="Create new order",
        tags=["Orders"]
    ),
    retrieve=extend_schema(
        summary="Order Details",
        description="Get specific order information",
        tags=["Orders"]
    ),
    update=extend_schema(
        summary="Update Order",
        description="Update order",
        tags=["Orders"]
    ),
    partial_update=extend_schema(
        summary="Partial Update Order",
        description="Partially update order",
        tags=["Orders"]
    ),
    destroy=extend_schema(
        summary="Delete Order",
        description="Delete order",
        tags=["Orders"]
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customer orders."""

    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrReadOnly)
    ordering = ('-created_at',)

    def get_queryset(self):
        """Filter orders by user (all for staff, own orders for users)."""
        if self.request.user.is_staff:
            return Order.objects.all().prefetch_related('items__product')
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        """Set the user when creating an order."""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Cancel Order",
        description="Cancel an order if it's in a cancellable status",
        tags=["Orders"]
    )
    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def cancel(self, request, pk=None):
        """Cancel an order if it's in a cancellable status."""
        order = self.get_object()

        if not order.can_be_canceled():
            return Response(
                {'error': 'This order cannot be canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.cancel_order()
            return Response(
                {'message': 'Order canceled successfully.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(
        summary="List Users",
        description="Get list of users (only own data for regular users)",
        tags=["Users"]
    ),
    create=extend_schema(
        summary="Create User (Admin Only)",
        description="Create new user account (admin only, "
                    "use /users/register/ for self-registration)",
        tags=["Users"]
    ),
    retrieve=extend_schema(
        summary="User Details",
        description="Get user information",
        tags=["Users"]
    ),
    update=extend_schema(
        summary="Update User",
        description="Update user data",
        tags=["Users"]
    ),
    partial_update=extend_schema(
        summary="Partial Update User",
        description="Partially update user data",
        tags=["Users"]
    ),
    destroy=extend_schema(
        summary="Delete User",
        description="Delete user",
        tags=["Users"]
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles."""

    queryset = user_model.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrReadOnly)
    ordering = ('username',)

    def get_queryset(self):
        """Filter users by current user or all for staff."""
        if self.request.user.is_staff:
            return user_model.objects.all()
        return user_model.objects.filter(id=self.request.user.id)

    @extend_schema(
        summary="My Profile",
        description="Get current user data",
        responses={200: UserSerializer},
        tags=["Users"]
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update My Profile",
        description="Update current user data",
        request=UserSerializer,
        responses={200: UserSerializer, 400: None},
        tags=["Users"]
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user profile."""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="User Registration",
    description="Create new user account",
    tags=["Authentication"],
    request=UserRegistrationSerializer,
    responses={201: UserSerializer, 400: None}
)
class UserRegistrationView(APIView):
    """View for user registration with password validation."""

    permission_classes = []

    def post(self, request):
        """Register a new user account."""
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data.pop('password')
            serializer.validated_data.pop('password_confirm')

            user = user_model.objects.create_user(**serializer.validated_data)
            user.set_password(password)
            user.save()

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Get Cart",
        description="Get current session cart contents",
        tags=["Cart"]
    ),
    create=extend_schema(
        summary="Add Item To Cart",
        description="Add product to cart with quantity",
        tags=["Cart"]
    ),
    update=extend_schema(
        summary="Update Cart Item",
        description="Update cart item quantity",
        tags=["Cart"]
    ),
    partial_update=extend_schema(
        summary="Partial Update Cart Item",
        description="Partially update cart item",
        tags=["Cart"]
    ),
    destroy=extend_schema(
        summary="Remove Cart Item",
        description="Remove item from cart",
        tags=["Cart"]
    ),
)
class CartViewSet(viewsets.ViewSet):
    """ViewSet for managing session-based shopping cart."""

    serializer_class = CartSerializer

    def list(self, request):
        """Get cart contents."""
        cart = SessionCart(request)
        cart_data = self._prepare_cart_data(cart)
        serializer = self.serializer_class(cart_data)
        return Response(serializer.data)

    def create(self, request):
        """Add item to cart."""
        cart = SessionCart(request)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
            cart.add(product, quantity)
            return self.list(request)  # Возвращаем обновлённую корзину
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        """Update cart item quantity."""
        cart = SessionCart(request)
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=pk)
            cart.add(product, quantity, override_quantity=True)
            return self.list(request)  # Возвращаем обновлённую корзину
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        """Remove item from cart."""
        cart = SessionCart(request)

        try:
            product = Product.objects.get(id=pk)
            cart.remove(product)
            return self.list(request)  # Возвращаем обновлённую корзину
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Clear Cart",
        description="Remove all items from cart",
        responses={200: {"description": "Cart cleared successfully"}},
        tags=["Cart"]
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart."""
        cart = SessionCart(request)
        cart.cart.clear()
        cart.save()
        return Response({'message': 'Cart cleared successfully'})

    def _prepare_cart_data(self, cart):
        """Prepare cart data for serialization."""
        items = []
        for item in cart:  # Используем __iter__() метод
            try:
                product = Product.objects.get(id=item['product_id'])
                item['product'] = product
                items.append(item)
            except Product.DoesNotExist:
                continue

        return {'items': items, 'cart_instance': cart}


@extend_schema(
    summary="Get Access Token",
    description="Get JWT tokens for authentication (use email)",
    tags=["Authentication"]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view that uses email instead of username."""
    from api.serializers import CustomTokenObtainPairSerializer
    serializer_class = CustomTokenObtainPairSerializer
