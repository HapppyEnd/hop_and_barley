from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')


app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
]
