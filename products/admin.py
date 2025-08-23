from django.contrib import admin
from products.models import Product, Category, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'category', 'price', 'image', 'is_active', 'stock',
        'created_at', 'updated_at',)
    list_filter = ('name', 'category', 'is_active', 'created_at', 'updated_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('name', 'parent', 'created_at', 'updated_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'updated_at',)
    list_filter = ('product', 'user', 'rating')
