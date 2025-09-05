from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'status', 'total_price', 'created_at',
                    'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for order items."""
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__id', 'product__name')
