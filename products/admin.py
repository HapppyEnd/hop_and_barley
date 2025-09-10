from django.contrib import admin

from products.models import Category, Product, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'category', 'price', 'image', 'is_active', 'stock',
        'created_at', 'updated_at',)
    list_filter = (
        'name', 'category', 'is_active', 'created_at', 'updated_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('name', 'parent', 'created_at', 'updated_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'user', 'rating', 'title', 'created_by_admin',
        'created_at', 'updated_at',)
    list_filter = (
        'product', 'user', 'rating', 'created_by_admin',
        'created_at', 'updated_at')
    search_fields = (
        'product__name', 'user__username', 'user__email', 'title', 'comment')
    list_editable = ('rating',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['delete_selected']

    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Admin Information', {
            'fields': ('created_by_admin',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Get queryset for admin list view."""
        return super().get_queryset(request).select_related('product', 'user')

    def get_form(self, request, obj=None, **kwargs):
        """Get form with admin user context."""
        form = super().get_form(request, obj, **kwargs)
        # Store request user for form validation
        form.request_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        """Save model with admin user tracking."""
        if not change:  # Only for new reviews
            # Mark that this review was created by admin
            obj.created_by_admin = True
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Allow admins to add reviews."""
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        """Allow admins to change reviews."""
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """Allow admins to delete reviews."""
        return request.user.is_superuser or request.user.is_staff
