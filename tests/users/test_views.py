import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserViews:
    """Test cases for user views."""
    
    @pytest.mark.view
    def test_login_view_get(self, client):
        """Test login view GET request."""
        response = client.get(reverse('users:login'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    @pytest.mark.view
    def test_login_view_post_valid(self, client):
        """Test login view POST with valid data."""
        UserFactory(email='test@example.com', password='testpass123')
        form_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        response = client.post(reverse('users:login'), data=form_data)
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_login_view_post_invalid(self, client):
        """Test login view POST with invalid data."""
        form_data = {
            'username': 'test@example.com',
            'password': 'wrongpass'
        }
        response = client.post(reverse('users:login'), data=form_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert not response.context['form'].is_valid()
    
    @pytest.mark.view
    def test_register_view_get(self, client):
        """Test register view GET request."""
        response = client.get(reverse('users:register'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    @pytest.mark.view
    def test_register_view_post_valid(self, client):
        """Test register view POST with valid data."""
        form_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = client.post(reverse('users:register'), data=form_data)
        assert response.status_code == 302
        assert User.objects.filter(email='newuser@example.com').exists()
    
    @pytest.mark.view
    def test_register_view_post_invalid(self, client):
        """Test register view POST with invalid data."""
        form_data = {
            'email': 'invalid-email',
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        response = client.post(reverse('users:register'), data=form_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert not response.context['form'].is_valid()
    
    @pytest.mark.view
    def test_profile_view_authenticated(self, client, user):
        """Test profile view for authenticated user."""
        client.force_login(user)
        response = client.get(reverse('users:account'))
        assert response.status_code == 200
    
    @pytest.mark.view
    def test_profile_view_unauthenticated(self, client):
        """Test profile view for unauthenticated user."""
        response = client.get(reverse('users:account'))
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_profile_update_post(self, client, user):
        """Test profile update POST request."""
        client.force_login(user)
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': user.email,
            'phone': '',
            'city': 'New City',
            'address': 'New Address'
        }
        response = client.post(reverse('users:account_edit'), data=form_data)
        assert response.status_code in [200, 302]
        
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'
        assert user.city == 'New City'
    
    @pytest.mark.view
    def test_logout_view(self, client, user):
        """Test logout view."""
        client.force_login(user)
        response = client.post(reverse('users:logout'))
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_password_change_view_authenticated(self, client, user):
        """Test password change view for authenticated user."""
        client.force_login(user)
        response = client.get(reverse('users:password_change'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    @pytest.mark.view
    def test_password_change_view_unauthenticated(self, client):
        """Test password change view for unauthenticated user."""
        response = client.get(reverse('users:password_change'))
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_password_change_post(self, client, user):
        """Test password change POST request."""
        client.force_login(user)
        form_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        response = client.post(
            reverse('users:password_change'), data=form_data)
        assert response.status_code == 302
        
        user.refresh_from_db()
        assert user.check_password('newpass123')
    
    @pytest.mark.view
    def test_forgot_password_view_get(self, client):
        """Test forgot password view GET request."""
        response = client.get(reverse('users:forgot_password'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    @pytest.mark.view
    def test_forgot_password_view_post(self, client):
        """Test forgot password view POST request."""
        UserFactory(email='test@example.com')
        form_data = {'email': 'test@example.com'}
        response = client.post(
            reverse('users:forgot_password'), data=form_data)
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_reset_password_view_get(self, client):
        """Test reset password view GET request."""
        response = client.get(reverse('users:reset_password'))
        assert response.status_code == 302
    
    @pytest.mark.view
    def test_reset_password_view_post(self, client):
        """Test reset password view POST request."""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        response = client.post(
            reverse('users:reset_password'), data=form_data)
        assert response.status_code in [200, 302]
