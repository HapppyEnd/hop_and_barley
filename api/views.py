from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.filters import ProductFilter
from api.permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from api.serializers import (CategorySerializer, OrderSerializer,
                             ProductSerializer, ReviewSerializer,
                             UserRegistrationSerializer, UserSerializer)
from orders.models import Order
from products.models import Category, Product, Review

user_model = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    )
    search_fields = ('name',)
    ordering_fields = ('name', 'created_at')
    ordering = ('name',)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products with filtering and search."""

    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
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
        
        # Check if user already reviewed this product
        if Review.objects.filter(user=user, product=product).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'product': 'You have already reviewed this product.'
            })
        
        # Check if user can review this product
        if not product.user_can_review(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only review products you have purchased and received."
            )
        
        serializer.save(user=user)


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

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view that uses email instead of username."""
    from api.serializers import CustomTokenObtainPairSerializer
    serializer_class = CustomTokenObtainPairSerializer
