from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F, Q, QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from orders.cart import Cart
from products.forms import ReviewForm
from products.models import Category, Product, Review


class ProductListView(ListView):
    """View for displaying product list with filtering and sorting."""
    template_name = 'products/product-list.html'
    context_object_name = 'products'
    paginate_by = settings.PRODUCTS_PER_PAGE

    def get_queryset(self) -> QuerySet:
        """Get filtered and sorted product queryset."""
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

        queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))

        sort_by = self.request.GET.get('sort', 'newest')

        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popularity':
            queryset = queryset.order_by(
                F('avg_rating').desc(nulls_last=True),
                '-created_at'
            )
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs) -> dict[str, any]:
        """Get context data for product list page."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        context['selected_categories'] = self.request.GET.getlist('category',
                                                                  [])
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'newest')

        return context


class ProductDetailView(DetailView):
    """View for displaying product details with reviews and cart info."""
    model = Product
    template_name = 'products/product-detail.html'
    slug_field = 'slug'
    context_object_name = 'product'

    def get_queryset(self) -> QuerySet:
        """Get active product queryset."""
        return Product.objects.filter(is_active=True).select_related(
            'category')

    def get_context_data(self, **kwargs) -> dict[str, any]:
        """Get context data for product detail page."""
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(
            product=self.object).select_related('user')

        context['REVIEW_ALREADY_REVIEWED'] = settings.REVIEW_ALREADY_REVIEWED
        context['REVIEW_AFTER_DELIVERY'] = settings.REVIEW_AFTER_DELIVERY
        context['LOGIN_TO_REVIEW'] = settings.LOGIN_TO_REVIEW

        cart = Cart(self.request)
        context['cart_quantity'] = cart.get_product_quantity(self.object.id)

        if self.request.user.is_authenticated:
            context['can_review'] = self.object.user_can_review(
                self.request.user
            )
            user_review = Review.objects.filter(
                product=self.object,
                user=self.request.user
            ).first()
            context['has_reviewed'] = user_review is not None
            context['user_review'] = user_review
        else:
            context['can_review'] = False
            context['has_reviewed'] = False
            context['user_review'] = None

        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """View for creating product reviews."""
    model = Review
    form_class = ReviewForm
    template_name = 'products/review_form.html'

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.product = None

    def get_success_url(self):
        """Return URL to redirect after successful review creation."""
        return reverse(
            'products:product-detail',
            kwargs={'slug': self.product.slug}
        )

    def get_form_kwargs(self):
        """Add user and product to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['product'] = self.product
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Check if user can review this product before processing."""
        self.product = self.get_object()

        if not self.product.user_can_review(request.user):
            messages.error(request, settings.REVIEW_DELIVERY_REQUIRED)
            return HttpResponseRedirect(
                reverse(
                    'products:product-detail',
                    kwargs={'slug': self.product.slug}
                )
            )
        if Review.objects.filter(
                product=self.product, user=request.user
        ).exists():
            messages.warning(request, settings.REVIEW_ALREADY_EXISTS)
            return HttpResponseRedirect(
                reverse(
                    'products:product-detail',
                    kwargs={'slug': self.product.slug}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get the product being reviewed."""
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def form_valid(self, form):
        """Set user and product before saving."""
        if not hasattr(self, 'product') or not self.product:
            self.product = self.get_object()

        form.instance.user = self.request.user
        form.instance.product = self.product
        form.instance.created_by_admin = self.request.user.is_staff

        messages.success(self.request, settings.REVIEW_SUCCESS_MESSAGE)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add product to context."""
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context


class ReviewUpdateView(UpdateView):
    """View for updating product reviews."""
    model = Review
    form_class = ReviewForm
    template_name = 'products/review_form.html'

    def get_object(self, queryset=None):
        """Get the review to update."""
        return get_object_or_404(
            Review,
            pk=self.kwargs['pk'],
            user=self.request.user,
            product__slug=self.kwargs['slug']
        )

    def get_success_url(self):
        """Redirect to product detail page after successful update."""
        return reverse_lazy(
            'products:product-detail',
            kwargs={'slug': self.object.product.slug})

    def form_valid(self, form):
        """Handle successful form submission."""
        messages.success(self.request, 'Review updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add product to context."""
        context = super().get_context_data(**kwargs)
        context['product'] = self.object.product
        return context
