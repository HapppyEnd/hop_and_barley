from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F, Sum

from products.models import Product


class Order(models.Model):
    """Модель заказа пользователя."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='orders') 
    status = models.CharField(choices=STATUS_CHOICES, default='pending',
                              max_length=20)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Order №{self.id} - status:{self.status}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    @property
    def total_price(self):
        """Возвращает общую сумму заказа."""
        total = self.items.aggregate(total=Sum(
            F('price') * F('quantity')))['total'] or 0
        return f"${total}"

    def reduce_stock(self):
        """Уменьшает остатки товаров при подтверждении заказа."""
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

    def restore_stock(self):
        """Восстанавливает остатки при отмене заказа."""
        with transaction.atomic():
            for item in self.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])


class OrderItem(models.Model):
    """Элемент заказа (товар с количеством и ценой)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1,
                                           validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (f'{self.quantity} x {self.product.name} '
                f'(Order №{self.order.id})')

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        """Сохраняет элемент заказа."""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

    @property
    def total(self):
        """Возвращает общую стоимость позиции (цена × количество)."""
        return f"${self.price * self.quantity}"