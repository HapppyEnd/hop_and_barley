from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import QuerySet

from orders.models import Order, OrderItem


class OrderItemInline(TabularInline):
    """Inline admin for order items.

    Provides inline editing of order items within the order admin interface.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('total',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders.

    Provides comprehensive order management with inline order items,
    filtering, searching, and display customization.
    """
    inlines = [OrderItemInline]
    list_display = (
        'id', 'user', 'status', 'total_price', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def get_queryset(self, request) -> QuerySet[Order]:
        """Get queryset with optimized queries."""
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for order items.

    Provides order item management with filtering and search capabilities.
    """
    list_display = (
        'id', 'order', 'product', 'quantity', 'price', 'total'
    )
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('total',)

    def get_queryset(self, request) -> QuerySet[OrderItem]:
        """Get queryset with optimized queries."""
        return super().get_queryset(request).select_related('order', 'product')
