import pytest
from rest_framework import status

from products.models import Product
from tests.factories import (CategoryFactory, ProductFactory)


@pytest.mark.django_db
class TestProductAPI:
    """Test cases for Product API endpoints."""

    @pytest.mark.api
    def test_product_list_api(self, api_client):
        """Test product list API endpoint."""
        ProductFactory.create_batch(5)

        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 5

    @pytest.mark.api
    def test_product_detail_api(self, api_client):
        """Test product detail API endpoint."""
        product = ProductFactory()

        response = api_client.get(f'/api/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name
        assert response.data['price'] == str(product.price)

    @pytest.mark.api
    def test_product_create_api_authenticated(self, admin_api_client):
        """Test product creation API for admin user."""
        category = CategoryFactory()
        product_data = {
            'name': 'Test API Product',
            'description': 'Test product created via API',
            'category_id': category.id,
            'price': '29.99',
            'stock': 100,
            'is_active': True
        }

        response = admin_api_client.post('/api/products/', data=product_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == product_data['name']

    @pytest.mark.api
    def test_product_create_api_unauthenticated(self, api_client):
        """Test product creation API for unauthenticated user."""
        category = CategoryFactory()
        product_data = {
            'name': 'Test API Product',
            'description': 'Test product created via API',
            'category_id': category.id,
            'price': '29.99',
            'stock': 100,
            'is_active': True
        }

        response = api_client.post('/api/products/', data=product_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_product_update_api_authenticated(self, admin_api_client):
        """Test product update API for admin user."""
        product = ProductFactory(name='Original Name')
        update_data = {'name': 'Updated Name'}

        response = admin_api_client.patch(
            f'/api/products/{product.id}/',
            data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'

    @pytest.mark.api
    def test_product_delete_api_authenticated(self, admin_api_client):
        """Test product deletion API for admin user."""
        product = ProductFactory()

        response = admin_api_client.delete(f'/api/products/{product.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(id=product.id).exists()

    @pytest.mark.api
    def test_product_filter_by_category(self, api_client):
        """Test product filtering by category."""
        category1 = CategoryFactory(name='Category 1', slug='category-1')
        category2 = CategoryFactory(name='Category 2', slug='category-2')

        ProductFactory.create_batch(3, category=category1)
        ProductFactory.create_batch(2, category=category2)

        response = api_client.get(f'/api/products/?category={category1.slug}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    @pytest.mark.api
    def test_product_search(self, api_client):
        """Test product search functionality."""
        ProductFactory(name='Test Product 1',
                       description='Unique description 1')
        ProductFactory(name='Another Product',
                       description='Unique description 2')
        ProductFactory(name='Test Product 2',
                       description='Unique description 3')

        response = api_client.get('/api/products/?search=Test')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
