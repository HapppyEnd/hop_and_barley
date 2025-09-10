from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Sum

from products.models import Product


class Order(models.Model):
    """User order model.

    Represents a customer order containing multiple products with
    quantities and prices. Tracks order status, shipping information,
    and timestamps.
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="User who placed the order"
    )
    status = models.CharField(
        choices=settings.ORDER_STATUS_CHOICES,
        default=settings.ORDER_STATUS_PENDING,
        max_length=20,
        help_text="Current status of the order"
    )
    shipping_address = models.TextField(
        help_text="Address where the order will be shipped"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the order was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the order was last updated"
    )

    def __str__(self) -> str:
        return f'{self.user.username} Order №{self.id} - status:{self.status}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    @property
    def total_price(self) -> str:
        """Return total order amount as formatted string."""
        total = self.items.aggregate(total=Sum(
            F('price') * F('quantity')))['total'] or 0
        return f"${total}"

    def reduce_stock(self) -> None:
        """Reduce product stock when order is confirmed."""
        with transaction.atomic():
            for item in self.items.select_for_update().all():
                product = item.product
                if item.quantity > product.stock:
                    raise ValidationError(
                        f"Not enough '{product.name}'. "
                        f"Available: {product.stock}"
                    )
                product.stock -= item.quantity
                product.save(update_fields=['stock'])

    def restore_stock(self) -> None:
        """Restore stock when order is canceled."""
        with transaction.atomic():
            for item in self.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])

    def can_be_canceled(self) -> bool:
        """Check if order can be canceled."""
        return self.status in settings.CANCELLABLE_STATUSES

    def cancel_order(self) -> None:
        """Cancel order and restore stock."""
        if not self.can_be_canceled():
            raise ValidationError("This order cannot be canceled")

        self.status = settings.ORDER_STATUS_CANCELED
        self.save()
        self.restore_stock()


class OrderItem(models.Model):
    """Order item (product with quantity and price).

    Represents a single product within an order with its quantity
    and price at the time of purchase.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Order this item belongs to"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product being ordered"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of the product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of purchase"
    )

    def __str__(self) -> str:
        return (f'{self.quantity} x {self.product.name} '
                f'(Order №{self.order.id})')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs) -> None:
        """Save order item with automatic price setting."""
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

    @property
    def total(self) -> str:
        """Return total item cost (price × quantity) as formatted string."""
        if self.price is None or self.quantity is None:
            return "$0.00"
        return f"${self.price * self.quantity}"
