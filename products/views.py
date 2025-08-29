from django.db.models import Avg, Q
from django.views.generic import DetailView, ListView

from products.models import Category, Product, Review


class ProductListView(ListView):
    template_name = 'products/product-list.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category')

        category_ids = self.request.GET.getlist('category')
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        sort_by = self.request.GET.get('sort', 'newest')

        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popularity':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-created_at')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        context['selected_categories'] = self.request.GET.getlist('category',
                                                                  [])
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'newest')

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
        
        # Добавляем информацию о корзине
        from orders.cart import Cart
        cart = Cart(self.request)
        context['cart_quantity'] = cart.get_product_quantity(self.object.id)
        
        return context
