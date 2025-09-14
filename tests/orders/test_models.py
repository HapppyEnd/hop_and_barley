from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from tests.factories import (DeliveredOrderFactory, OrderFactory,
                             OrderItemFactory, PendingOrderFactory,
                             ProductFactory, UserFactory)


@pytest.mark.django_db
class TestOrderModel:
    """Test cases for Order model."""

    @pytest.mark.model
    def test_order_creation(self):
        """Test order creation with required fields."""
        user = UserFactory()
        order = OrderFactory(user=user, status='pending')

        assert order.user == user
        assert order.status == 'pending'
        assert order.shipping_address is not None
        assert order.created_at is not None
        assert order.updated_at is not None

    @pytest.mark.model
    def test_order_str_representation(self):
        """Test order string representation."""
        user = UserFactory(username='testuser')
        order = OrderFactory(user=user, status='pending')

        expected = 'testuser Order №1 - status:pending'
        assert str(order) == expected

    @pytest.mark.model
    def test_order_total_price_empty(self):
        """Test order total price with no items."""
        order = OrderFactory()
        assert order.total_price == '$0.00'

    @pytest.mark.model
    def test_order_total_price_with_items(self):
        """Test order total price calculation with items."""
        order = OrderFactory()
        product1 = ProductFactory(price=Decimal('10.00'))
        product2 = ProductFactory(price=Decimal('20.00'))

        OrderItemFactory(order=order, product=product1, quantity=2,
                         price=Decimal('10.00'))
        OrderItemFactory(order=order, product=product2, quantity=1,
                         price=Decimal('20.00'))

        assert order.total_price == '$40.00'

    @pytest.mark.model
    def test_order_can_be_canceled_pending(self):
        """Test order can be canceled when pending."""
        order = PendingOrderFactory()
        assert order.can_be_canceled() is True

    @pytest.mark.model
    def test_order_can_be_canceled_delivered(self):
        """Test order cannot be canceled when delivered."""
        order = DeliveredOrderFactory()
        assert order.can_be_canceled() is False

    @pytest.mark.model
    def test_order_cancel_order_success(self):
        """Test successful order cancellation."""
        order = PendingOrderFactory()
        order.cancel_order()

        assert order.status == 'canceled'

    @pytest.mark.model
    def test_order_cancel_order_failure(self):
        """Test order cancellation failure for non-cancelable order."""
        order = DeliveredOrderFactory()

        with pytest.raises(ValidationError):
            order.cancel_order()

    @pytest.mark.model
    def test_order_reduce_stock_success(self):
        """Test successful stock reduction."""
        product = ProductFactory(stock=10)
        order = OrderFactory()
        OrderItemFactory(order=order, product=product, quantity=5,
                         price=product.price)

        order.reduce_stock()

        product.refresh_from_db()
        assert product.stock == 5

    @pytest.mark.model
    def test_order_reduce_stock_insufficient(self):
        """Test stock reduction with insufficient stock."""
        product = ProductFactory(stock=5)
        order = OrderFactory()
        OrderItemFactory(order=order, product=product, quantity=10,
                         price=product.price)

        with pytest.raises(ValidationError):
            order.reduce_stock()

    @pytest.mark.model
    def test_order_restore_stock(self):
        """Test stock restoration when order is canceled."""
        product = ProductFactory(stock=5)
        order = OrderFactory()
        OrderItemFactory(order=order, product=product, quantity=3,
                         price=product.price)

        order.reduce_stock()
        product.refresh_from_db()
        assert product.stock == 2
        order.restore_stock()
        product.refresh_from_db()
        assert product.stock == 5


@pytest.mark.django_db
class TestOrderItemModel:
    """Test cases for OrderItem model."""

    @pytest.mark.model
    def test_order_item_creation(self):
        """Test order item creation with required fields."""
        order = OrderFactory()
        product = ProductFactory(price=Decimal('25.00'))
        order_item = OrderItemFactory(
            order=order,
            product=product,
            quantity=2,
            price=Decimal('25.00')
        )

        assert order_item.order == order
        assert order_item.product == product
        assert order_item.quantity == 2
        assert order_item.price == Decimal('25.00')

    @pytest.mark.model
    def test_order_item_str_representation(self):
        """Test order item string representation."""
        product = ProductFactory(name='Test Product')
        order = OrderFactory()
        order_item = OrderItemFactory(
            order=order,
            product=product,
            quantity=3
        )

        expected = '3 x Test Product (Order №1)'
        assert str(order_item) == expected

    @pytest.mark.model
    def test_order_item_total_property(self):
        """Test order item total property calculation."""
        order_item = OrderItemFactory(
            quantity=3,
            price=Decimal('15.50')
        )

        assert order_item.total == '$46.50'

    @pytest.mark.model
    def test_order_item_total_with_zero_values(self):
        """Test order item total with zero values."""
        order_item = OrderItemFactory(
            quantity=0,
            price=Decimal('0.00')
        )

        assert order_item.total == '$0.00'

    @pytest.mark.model
    def test_order_item_auto_price_setting(self):
        """Test order item automatic price setting from product."""
        product = ProductFactory(price=Decimal('30.00'))
        order = OrderFactory()

        order_item = OrderItemFactory(
            order=order,
            product=product,
            quantity=1,
            price=None
        )

        assert order_item.price == Decimal('30.00')
