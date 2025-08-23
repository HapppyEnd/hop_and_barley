from django.views.generic import ListView, DetailView

from products.models import Product, Category, Review


class ProductListView(ListView):
    queryset = Product.objects.filter(
        is_active=True).select_related('category')
    template_name = 'products/product-list.html'
    slug_field = 'slug'
    context_object_name = 'products'
    paginate_by = 3
    ordering = ('-created_at',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product-detail.html'
    slug_field = 'slug'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(
            product=self.object).select_related('user')
        return context

