from django.urls import path
from django.views.generic import TemplateView

from products.views import ProductListView, ProductDetailView

app_name = 'products'
urlpatterns = [
    path('guides_recipes/',
         TemplateView.as_view(template_name='products/guides-recipes.html'),
         name='guides_recipes'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),

]
