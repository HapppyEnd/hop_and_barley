from django.urls import path
from django.views.generic import TemplateView

app_name = 'products'
urlpatterns = [
    path('guides_recipes/',
         TemplateView.as_view(template_name='products/guides-recipes.html'),
         name='guides_recipes'),
]
