from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (CategoryViewSet, CustomTokenObtainPairView, OrderViewSet,
                    ProductViewSet, ReviewViewSet, UserRegistrationView,
                    UserViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path(
        'auth/token/', CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'auth/token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'auth/token/verify/', TokenVerifyView.as_view(),
        name='token_verify'
    ),
    path(
        'users/register/', UserRegistrationView.as_view(),
        name='user_register'
    ),
    path('', include(router.urls)),
]
