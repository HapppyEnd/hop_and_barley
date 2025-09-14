import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test cases for Authentication API endpoints."""

    @pytest.mark.api
    def test_login_api_valid_credentials(self, api_client, user):
        """Test login API with valid credentials."""
        login_data = {
            'email': user.email,
            'password': 'testpass123'
        }

        response = api_client.post('/api/auth/token/', data=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    @pytest.mark.api
    def test_login_api_invalid_credentials(self, api_client):
        """Test login API with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post('/api/auth/token/', data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_token_refresh_api(self, api_client, user):
        """Test token refresh API."""
        login_data = {
            'email': user.email,
            'password': 'testpass123'
        }
        login_response = api_client.post('/api/auth/token/', data=login_data)
        refresh_token = login_response.data['refresh']

        refresh_data = {'refresh': refresh_token}
        response = api_client.post(
            '/api/auth/token/refresh/', data=refresh_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    @pytest.mark.api
    def test_user_registration_api(self, api_client):
        """Test user registration API."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

        response = api_client.post('/api/users/register/', data=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == user_data['email']
        assert response.data['username'] == user_data['username']

    @pytest.mark.api
    def test_user_profile_api_authenticated(
            self, authenticated_api_client, user):
        """Test user profile API for authenticated user."""
        response = authenticated_api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username

    @pytest.mark.api
    def test_user_profile_api_unauthenticated(self, api_client):
        """Test user profile API for unauthenticated user."""
        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    def test_user_profile_update_api_authenticated(
            self, authenticated_api_client, user):
        """Test user profile update API for authenticated user."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'city': 'New City'
        }

        response = authenticated_api_client.patch(
            '/api/users/update_me/',
            data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
        assert response.data['city'] == 'New City'
