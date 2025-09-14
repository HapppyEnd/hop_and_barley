import pytest
from django.urls import resolve, reverse

from tests.factories import ProductFactory


@pytest.mark.django_db
class TestProductURLs:
    """Test cases for product URL patterns."""

    @pytest.mark.url
    def test_product_list_url(self, client):
        """Test product list URL resolves correctly."""
        url = reverse('products:product-list')
        assert url == '/products/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_product_detail_url(self, client):
        """Test product detail URL resolves correctly."""
        product = ProductFactory(slug='test-product')
        url = reverse('products:product-detail', args=[product.slug])
        assert url == f'/products/{product.slug}/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_add_review_url(self, client, user):
        """Test add review URL resolves correctly."""
        product = ProductFactory()
        client.force_login(user)

        url = reverse('products:review-create', args=[product.slug])
        assert url == f'/products/{product.slug}/review/'

        response = client.get(url)
        assert response.status_code in [200, 302, 404]

    @pytest.mark.url
    def test_url_patterns_exist(self):
        """Test that all expected URL patterns exist."""
        simple_urls = ['products:product-list']
        for url_name in simple_urls:
            try:
                url = reverse(url_name)
                assert url is not None
            except Exception as e:
                pytest.fail(f"URL pattern '{url_name}' not found: {e}")
        product = ProductFactory()
        complex_urls = [
            ('products:product-detail', [product.slug]),
            ('products:review-create', [product.slug]),
        ]
        for url_name, args in complex_urls:
            try:
                url = reverse(url_name, args=args)
                assert url is not None
            except Exception as e:
                pytest.fail(f"URL pattern '{url_name}' not found: {e}")

    @pytest.mark.url
    def test_url_resolution(self):
        """Test URL resolution for product patterns."""
        resolver = resolve('/products/')
        assert resolver.view_name == 'products:product-list'
        resolver = resolve('/products/test-product/')
        assert resolver.view_name == 'products:product-detail'

    @pytest.mark.url
    def test_dynamic_urls(self, client):
        """Test dynamic URL patterns with actual data."""
        product = ProductFactory(slug='dynamic-product')
        url = reverse('products:product-detail', args=[product.slug])
        response = client.get(url)
        assert response.status_code == 200
