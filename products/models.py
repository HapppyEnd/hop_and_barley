from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.mixins import SlugMixin


class JournalizedModel(models.Model):
    """Base model with created_at and updated_at fields.

    Provides automatic timestamp tracking for model instances.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class Category(JournalizedModel, SlugMixin):
    """Product category model with hierarchical structure.

    Represents product categories that can have parent-child relationships.
    """
    name = models.CharField(
        max_length=100,
        help_text="Category name"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category for hierarchical structure"
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save category with unique slug.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.generate_unique_slug(Category)
        super().save(*args, **kwargs)


class Product(JournalizedModel, SlugMixin):
    """Product model with inventory and review capabilities.

    Represents a product in the store with pricing, inventory, and review
    features.
    """
    name = models.CharField(
        max_length=100,
        help_text="Product name"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        help_text="Product description"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Product category"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price"
    )
    image = models.ImageField(
        upload_to='product_images',
        blank=True,
        null=True,
        default='product_images/default.png',
        help_text="Product image"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the product is available for purchase"
    )
    stock = models.PositiveIntegerField(
        help_text="Available stock quantity"
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save product with unique slug.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.generate_unique_slug(Product)
        super().save(*args, **kwargs)

    @property
    def get_image_url(self) -> str:
        """Return image URL or default image.

        Returns:
            Image URL or default product image path
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/img/products/default_product.png'

    def user_can_review(self, user) -> bool:
        """Check if user can review this product.

        Args:
            user: User instance to check

        Returns:
            True if user can review, False otherwise
        """
        if not user.is_authenticated:
            return False

        from orders.models import OrderItem
        return OrderItem.objects.filter(
            order__user=user,
            order__status__in=['paid', 'shipped', 'delivered'],
            product=self
        ).exists()


class Review(JournalizedModel):
    """Product review model with validation.

    Represents a user's review of a product with rating and comment.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Product being reviewed"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="User who wrote the review"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Enter a rating between 1-5'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional review title"
    )
    comment = models.TextField(
        help_text="Review comment"
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)
        unique_together = ('user', 'product')

    def __str__(self) -> str:
        return f'{self.user.username}: {self.rating} - {self.comment}'

    def clean(self) -> None:
        """Validate that user purchased the product.

        Raises:
            ValidationError: If user hasn't purchased the product
        """
        super().clean()
        if not self.product.user_can_review(self.user):
            raise ValidationError(
                'You can only review products you have purchased.'
            )

    def save(self, *args, **kwargs) -> None:
        """Validate before saving.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.clean()
        super().save(*args, **kwargs)
