from django.urls import path
from django.views.generic import TemplateView

from products.views import (ProductDetailView, ProductListView,
                            ReviewCreateView, ReviewUpdateView)

app_name = 'products'
urlpatterns = [
    path('guides_recipes/',
         TemplateView.as_view(template_name='products/guides-recipes.html'),
         name='guides_recipes'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(),
         name='product-detail'),
    path('products/<slug:slug>/review/', ReviewCreateView.as_view(),
         name='review-create'),
    path('products/<slug:slug>/review/<int:pk>/edit/',
         ReviewUpdateView.as_view(), name='review-update'),
    path(
        'contact/',
        TemplateView.as_view(template_name='products/contact.html'),
        name='contact'),
    path('faq/', TemplateView.as_view(template_name='products/faq.html'),
         name='faq'),
    path(
        'community/',
        TemplateView.as_view(template_name='products/community.html'),
        name='community'),
    path('resources/',
         TemplateView.as_view(template_name='products/resources.html'),
         name='resources'),
    path('license/',
         TemplateView.as_view(template_name='products/license.html'),
         name='license'),
]
