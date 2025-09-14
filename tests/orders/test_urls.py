import pytest
from django.urls import resolve, reverse

from tests.factories import OrderFactory, ProductFactory


@pytest.mark.django_db
class TestOrderURLs:
    """Test cases for order URL patterns."""

    @pytest.mark.url
    def test_cart_url(self, client):
        """Test cart URL resolves correctly."""
        url = reverse('orders:cart_detail')
        assert url == '/orders/cart/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_cart_add_url(self, client, product):
        """Test cart add URL resolves correctly."""
        url = reverse('orders:cart_add', args=[product.id])
        assert url == f'/orders/cart/add/{product.id}/'

        response = client.post(url, {'quantity': 1, 'override': False})
        assert response.status_code == 302

    @pytest.mark.url
    def test_cart_remove_url(self, client, product):
        """Test cart remove URL resolves correctly."""
        url = reverse('orders:cart_remove', args=[product.id])
        assert url == f'/orders/cart/remove/{product.id}/'

        response = client.post(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_checkout_url_authenticated(self, client, user, product):
        """Test checkout URL resolves correctly for authenticated user."""
        client.force_login(user)

        client.post(reverse('orders:cart_add', args=[product.id]), {
            'quantity': 1,
            'override': False
        })

        url = reverse('orders:checkout')
        assert url == '/orders/checkout/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_checkout_url_unauthenticated(self, client):
        """Test checkout URL redirects for unauthenticated user."""
        url = reverse('orders:checkout')
        assert url == '/orders/checkout/'

        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_order_list_url_authenticated(self, client, user):
        """Test order list URL resolves correctly for authenticated user."""
        client.force_login(user)
        url = reverse('orders:order_list')
        assert url == '/orders/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_order_list_url_unauthenticated(self, client):
        """Test order list URL redirects for unauthenticated user."""
        url = reverse('orders:order_list')
        assert url == '/orders/'

        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_order_detail_url_authenticated(self, client, user):
        """Test order detail URL resolves correctly for authenticated user."""
        client.force_login(user)
        order = OrderFactory(user=user)
        url = reverse('orders:order_detail', args=[order.id])
        assert url == f'/orders/{order.id}/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_order_cancel_url_authenticated(self, client, user):
        """Test order cancel URL resolves correctly for authenticated user."""
        client.force_login(user)
        order = OrderFactory(user=user)
        url = reverse('orders:cancel_order', args=[order.id])
        assert url == f'/orders/{order.id}/cancel/'

        response = client.post(url)
        assert response.status_code in [200, 302, 400]

    @pytest.mark.url
    def test_url_patterns_exist(self):
        """Test that all expected URL patterns exist."""
        expected_urls = [
            'orders:cart_detail',
            'orders:checkout',
            'orders:order_list',
        ]

        for url_name in expected_urls:
            try:
                url = reverse(url_name)
                assert url is not None
            except Exception as e:
                pytest.fail(f"URL pattern '{url_name}' not found: {e}")

    @pytest.mark.url
    def test_url_resolution(self):
        """Test URL resolution for order patterns."""
        # Test cart URL resolution
        resolver = resolve('/orders/cart/')
        assert resolver.view_name == 'orders:cart_detail'

        # Test checkout URL resolution
        resolver = resolve('/orders/checkout/')
        assert resolver.view_name == 'orders:checkout'

        # Test order list URL resolution
        resolver = resolve('/orders/')
        assert resolver.view_name == 'orders:order_list'

    @pytest.mark.url
    def test_dynamic_urls(self, client, user):
        """Test dynamic URL patterns with actual data."""
        client.force_login(user)

        order = OrderFactory(user=user)
        url = reverse('orders:order_detail', args=[order.id])
        response = client.get(url)
        assert response.status_code == 200

        url = reverse('orders:cancel_order', args=[order.id])
        response = client.post(url)
        assert response.status_code in [200, 302, 400]

    @pytest.mark.url
    def test_cart_urls_with_products(self, client):
        """Test cart URLs with actual products."""
        product = ProductFactory()

        url = reverse('orders:cart_add', args=[product.id])
        response = client.post(url, {'quantity': 1, 'override': False})
        assert response.status_code == 302

        url = reverse('orders:cart_remove', args=[product.id])
        response = client.post(url)
        assert response.status_code == 302
