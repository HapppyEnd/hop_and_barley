from django.views.generic import ListView, DetailView, TemplateView

from products.models import Product, Category, Review


class ProductListView(ListView):
    queryset = Product.objects.filter(is_active=True)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(product=self.object)
        return context