from django.views.generic import ListView, DetailView, TemplateView

from products.models import Product, Category
# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = 'products/product-list.html'
    slug_field = 'slug'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product-detail.html'
    slug_field = 'slug'
    context_object_name = 'product'
