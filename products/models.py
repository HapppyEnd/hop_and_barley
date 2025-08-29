from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.mixins import SlugMixin


class JournalizedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class Category(JournalizedModel, SlugMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True,
                               blank=True, related_name='subcategories')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.generate_unique_slug(Category)
        super().save(*args, **kwargs)


class Product(JournalizedModel, SlugMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images', blank=True,
                              null=True, default='product_images/default.png')
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.generate_unique_slug(Product)
        super().save(*args, **kwargs)
    
    @property
    def get_image_url(self):
        """Возвращает URL изображения или изображение по умолчанию"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/img/products/default_product.png'

    def user_can_review(self, user):
        """Проверяет, может ли пользователь оставить отзыв на товар."""
        if not user.is_authenticated:
            return False
        
        # Проверяем, есть ли у пользователя заказы с этим товаром
        from orders.models import OrderItem
        return OrderItem.objects.filter(
            order__user=user,
            order__status__in=['paid', 'shipped', 'delivered'],
            product=self
        ).exists()


class Review(JournalizedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Enter a rating between 1-5')
    title = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField()

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username}: {self.rating} - {self.comment}'

    def clean(self):
        """Проверяет, что пользователь покупал товар."""
        super().clean()
        if not self.product.user_can_review(self.user):
            raise ValidationError(
                'You can only review products you have purchased.'
            )

    def save(self, *args, **kwargs):
        """Проверяет валидность перед сохранением."""
        self.clean()
        super().save(*args, **kwargs)
