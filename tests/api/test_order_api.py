import pytest
from rest_framework import status

from tests.factories import OrderFactory, UserFactory


@pytest.mark.django_db
class TestOrderAPI:
    """Test cases for Order API endpoints."""

    @pytest.mark.api
    def test_order_list_api_authenticated(
            self, authenticated_api_client, user):
        """Test order list API for authenticated user."""
        OrderFactory.create_batch(3, user=user)

        response = authenticated_api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 3

    @pytest.mark.api
    def test_order_list_api_unauthenticated(self, api_client):
        """Test order list API for unauthenticated user."""
        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_order_detail_api_authenticated(
            self, authenticated_api_client, user):
        """Test order detail API for authenticated user."""
        order = OrderFactory(user=user)

        response = authenticated_api_client.get(f'/api/orders/{order.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id
        assert response.data['status'] == order.status

    @pytest.mark.api
    def test_order_detail_api_other_user(self, authenticated_api_client, user):
        """Test order detail API for other user's order."""
        other_user = UserFactory()
        order = OrderFactory(user=other_user)

        response = authenticated_api_client.get(f'/api/orders/{order.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.api
    def test_order_create_api_authenticated(
            self, authenticated_api_client, user, product):
        """Test order creation API for authenticated user."""
        order_data = {
            'shipping_address': '123 Test St, Test City, TC 12345',
            'items': [
                {
                    'product': product.id,
                    'quantity': 2,
                    'price': str(product.price)
                }
            ]
        }

        response = authenticated_api_client.post(
            '/api/orders/', data=order_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert (response.data['shipping_address'] ==
                order_data['shipping_address'])

    @pytest.mark.api
    def test_order_update_status_api_admin(self, admin_api_client, user):
        """Test order status update API for admin user."""
        order = OrderFactory(user=user, status='pending')
        update_data = {'status': 'paid'}

        response = admin_api_client.patch(
            f'/api/orders/{order.id}/',
            data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'paid'

    @pytest.mark.api
    def test_order_cancel_api_authenticated(
            self, authenticated_api_client, user):
        """Test order cancellation API for authenticated user."""
        order = OrderFactory(user=user, status='pending')

        response = authenticated_api_client.post(
            f'/api/orders/{order.id}/cancel/')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'canceled successfully' in response.data['message']

    @pytest.mark.api
    def test_order_filter_by_status(self, authenticated_api_client, user):
        """Test order filtering by status."""
        OrderFactory.create_batch(2, user=user, status='pending')
        OrderFactory.create_batch(3, user=user, status='delivered')

        response = authenticated_api_client.get('/api/orders/?status=pending')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
