import pytest
from django.urls import reverse

from tests.factories import (DeliveredOrderFactory, OrderFactory,
                             OrderItemFactory, PendingOrderFactory,
                             UserFactory)


@pytest.mark.django_db
class TestOrderViews:
    """Test cases for order views."""

    @pytest.mark.view
    def test_cart_view_get(self, client):
        """Test cart view GET request."""
        response = client.get(reverse('orders:cart_detail'))
        assert response.status_code == 200
        assert 'cart' in response.context

    @pytest.mark.view
    def test_cart_add_view_post(self, client, product):
        """Test cart add view POST request."""
        response = client.post(reverse('orders:cart_add', args=[product.id]), {
            'quantity': 2,
            'override': False
        })
        assert response.status_code == 302

    @pytest.mark.view
    def test_cart_remove_view_post(self, client, product):
        """Test cart remove view POST request."""
        session = client.session
        session['cart'] = {
            str(product.id): {'quantity': 2, 'price': str(product.price)}}
        session.save()

        response = client.post(reverse(
            'orders:cart_remove', args=[product.id]))
        assert response.status_code == 302

    @pytest.mark.view
    def test_checkout_view_authenticated(self, client, user, product):
        """Test checkout view for authenticated user."""
        client.force_login(user)

        client.post(reverse('orders:cart_add', args=[product.id]), {
            'quantity': 1,
            'override': False
        })

        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 200
        assert 'cart' in response.context

    @pytest.mark.view
    def test_checkout_view_unauthenticated(self, client):
        """Test checkout view for unauthenticated user."""
        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 302

    @pytest.mark.view
    def test_checkout_view_post_valid(
            self, client, user, product, monkeypatch):
        """Test checkout view POST with valid data."""
        monkeypatch.setattr(
            'orders.views.process_payment', lambda *args, **kwargs: True)
        client.force_login(user)

        session = client.session
        session['cart'] = {
            str(product.id): {'quantity': 2, 'price': str(product.price)}}
        session.save()

        form_data = {
            'shipping_address': '123 Test St, Test City, TC 12345',
            'payment_method': 'card',
            'card_number': '4111111111111111',
            'expiry_date': '12/25',
            'cvv': '123',
            'card_holder': 'Test User'
        }

        response = client.post(reverse('orders:checkout'), data=form_data)
        assert response.status_code == 302

    @pytest.mark.view
    def test_order_list_view_authenticated(self, client, user):
        """Test order list view for authenticated user."""
        client.force_login(user)
        OrderFactory.create_batch(3, user=user)

        response = client.get(reverse('orders:order_list'))
        assert response.status_code == 200
        assert 'orders' in response.context
        assert len(response.context['orders']) == 3

    @pytest.mark.view
    def test_order_list_view_unauthenticated(self, client):
        """Test order list view for unauthenticated user."""
        response = client.get(reverse('orders:order_list'))
        assert response.status_code == 302

    @pytest.mark.view
    def test_order_detail_view_authenticated(self, client, user):
        """Test order detail view for authenticated user."""
        client.force_login(user)
        order = OrderFactory(user=user)

        response = client.get(reverse('orders:order_detail', args=[order.id]))
        assert response.status_code == 200
        assert 'order' in response.context
        assert response.context['order'] == order

    @pytest.mark.view
    def test_order_detail_view_other_user(self, client, user):
        """Test order detail view for other user's order."""
        other_user = UserFactory()
        client.force_login(user)
        order = OrderFactory(user=other_user)

        response = client.get(reverse('orders:order_detail', args=[order.id]))
        assert response.status_code == 404

    @pytest.mark.view
    def test_order_cancel_view_success(self, client, user):
        """Test order cancel view for cancelable order."""
        client.force_login(user)
        order = PendingOrderFactory(user=user)

        response = client.post(reverse('orders:cancel_order', args=[order.id]))
        assert response.status_code == 302

        order.refresh_from_db()
        assert order.status == 'canceled'

    @pytest.mark.view
    def test_order_cancel_view_failure(self, client, user):
        """Test order cancel view for non-cancelable order."""
        client.force_login(user)
        order = DeliveredOrderFactory(user=user)

        response = client.post(reverse('orders:cancel_order', args=[order.id]))
        assert response.status_code == 400


@pytest.mark.django_db
class TestOrderIntegration:
    """Integration tests for order functionality."""

    @pytest.mark.integration
    def test_complete_order_flow(self, client, user, product, monkeypatch):
        """Test complete order flow from cart to order creation."""
        monkeypatch.setattr(
            'orders.views.process_payment', lambda *args, **kwargs: True)
        client.force_login(user)

        response = client.post(reverse('orders:cart_add', args=[product.id]), {
            'quantity': 2,
            'override': False
        })
        assert response.status_code == 302

        response = client.get(reverse('orders:cart_detail'))
        assert response.status_code == 200
        assert 'cart' in response.context

        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 200

        form_data = {
            'shipping_address': '123 Test St, Test City, TC 12345',
            'payment_method': 'card',
            'card_number': '4111111111111111',
            'expiry_date': '12/25',
            'cvv': '123',
            'card_holder': 'Test User'
        }

        response = client.post(reverse('orders:checkout'), data=form_data)
        assert response.status_code == 302

        from orders.models import Order
        assert Order.objects.filter(user=user).exists()
        order = Order.objects.get(user=user)
        assert order.status == 'paid'
        assert order.items.count() == 1

        order_item = order.items.first()
        assert order_item.product == product
        assert order_item.quantity == 2
        assert float(order_item.price) == float(product.price)

    @pytest.mark.integration
    def test_order_cancellation_flow(self, client, user, product):
        """Test order cancellation flow."""
        client.force_login(user)

        order = PendingOrderFactory(user=user)
        OrderItemFactory(
            order=order, product=product, quantity=2, price=product.price)

        initial_stock = product.stock

        response = client.post(reverse('orders:cancel_order', args=[order.id]))
        assert response.status_code == 302

        order.refresh_from_db()
        assert order.status == 'canceled'

        product.refresh_from_db()
        assert product.stock == initial_stock + 2
