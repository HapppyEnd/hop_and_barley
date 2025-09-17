import pytest
from rest_framework import status

from tests.factories import CategoryFactory, ProductFactory, UserFactory


@pytest.mark.django_db
class TestAPIWorkflow:
    """Integration tests for API workflow."""

    @pytest.mark.integration
    def test_api_authentication_workflow(self, api_client):
        """Test API authentication workflow."""
        UserFactory(email='apiuser@example.com', password='testpass123')

        login_data = {
            'email': 'apiuser@example.com',
            'password': 'testpass123'
        }

        response = api_client.post('/api/auth/token/', data=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        access_token = response.data['access']

        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'apiuser@example.com'

    @pytest.mark.integration
    def test_api_product_workflow(self, api_client):
        """Test API product workflow."""
        category = CategoryFactory(
            name='Test Category', slug='test-category'
        )
        products = ProductFactory.create_batch(
            5, category=category, is_active=True
        )

        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

        assert response.data['count'] == 5

        product = products[0]
        response = api_client.get(f'/api/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name

        response = api_client.get(
            f'/api/products/?category={category.slug}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

        response = api_client.get('/api/products/?search=Test')
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.integration
    def test_api_order_workflow(self, api_client):
        """Test API order workflow."""
        UserFactory(email='orderuser@example.com', password='testpass123')
        product = ProductFactory(price=25.00)

        login_data = {
            'email': 'orderuser@example.com',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/token/', data=login_data)
        access_token = response.data['access']
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        order_data = {
            'shipping_address': (
                '123 API Test St, Test City, TC 12345'
            ),
            'items': [
                {
                    'product': product.id,
                    'quantity': 2,
                    'price': str(product.price)
                }
            ]
        }

        response = api_client.post(
            '/api/orders/', data=order_data, format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert (response.data['shipping_address'] ==
                order_data['shipping_address'])

        order_id = response.data['id']

        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

        response = api_client.get(f'/api/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order_id

        response = api_client.post(f'/api/orders/{order_id}/cancel/')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'canceled successfully' in response.data['message']

    @pytest.mark.integration
    def test_api_pagination_workflow(self, api_client):
        """Test API pagination workflow."""
        category = CategoryFactory()
        ProductFactory.create_batch(25, category=category)

        response = api_client.get('/api/products/')
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 25

        response = api_client.get('/api/products/?page=2')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    @pytest.mark.integration
    def test_api_filtering_workflow(self, api_client):
        """Test API filtering workflow."""
        category1 = CategoryFactory(
            name='Category 1', slug='category-1'
        )
        category2 = CategoryFactory(
            name='Category 2', slug='category-2'
        )

        ProductFactory.create_batch(
            2, category=category1, price=10.00, is_active=True
        )
        ProductFactory.create_batch(
            3, category=category2, price=50.00, is_active=True
        )

        response = api_client.get(
            f'/api/products/?category={category1.slug}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

        response = api_client.get(
            '/api/products/?min_price=20&max_price=80'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

        response = api_client.get('/api/products/?is_active=true')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

    @pytest.mark.integration
    def test_api_error_handling_workflow(self, api_client):
        """Test API error handling workflow."""
        response = api_client.get('/api/products/999999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = api_client.post('/api/products/', data={
            'name': 'Test Product',
            'price': '29.99'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.integration
    def test_api_token_refresh_workflow(self, api_client):
        """Test API token refresh workflow."""
        UserFactory(
            email='refreshuser@example.com', password='testpass123'
        )

        login_data = {
            'email': 'refreshuser@example.com',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/token/', data=login_data)
        refresh_token = response.data['refresh']

        refresh_data = {'refresh': refresh_token}
        response = api_client.post(
            '/api/auth/token/refresh/', data=refresh_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

        new_access_token = response.data['access']
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {new_access_token}'
        )

        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'refreshuser@example.com'
