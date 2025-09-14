import pytest
from django.urls import resolve, reverse


@pytest.mark.django_db
class TestUserURLs:
    """Test cases for user URL patterns."""

    @pytest.mark.url
    def test_login_url(self, client):
        """Test login URL resolves correctly."""
        url = reverse('users:login')
        assert url == '/users/login/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_register_url(self, client):
        """Test register URL resolves correctly."""
        url = reverse('users:register')
        assert url == '/users/register/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_profile_url_authenticated(self, client, user):
        """Test profile URL resolves correctly for authenticated user."""
        client.force_login(user)
        url = reverse('users:account')
        assert url == '/users/account/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_profile_url_unauthenticated(self, client):
        """Test profile URL redirects for unauthenticated user."""
        url = reverse('users:account')
        assert url == '/users/account/'

        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_logout_url(self, client, user):
        """Test logout URL resolves correctly."""
        client.force_login(user)
        url = reverse('users:logout')
        assert url == '/users/logout/'

        response = client.post(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_password_change_auth(self, client, user):
        """Test password change URL for authenticated user."""
        client.force_login(user)
        url = reverse('users:password_change')
        assert url == '/users/password/change/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_password_change_url_unauthenticated(self, client):
        """Test password change URL redirects for unauthenticated user."""
        url = reverse('users:password_change')
        assert url == '/users/password/change/'

        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_forgot_password_url(self, client):
        """Test forgot password URL resolves correctly."""
        url = reverse('users:forgot_password')
        assert url == '/users/forgot-password/'

        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.url
    def test_reset_password_url(self, client):
        """Test reset password URL resolves correctly."""
        url = reverse('users:reset_password')
        assert url == '/users/reset-password/'

        response = client.get(url)
        assert response.status_code == 302

    @pytest.mark.url
    def test_url_patterns_exist(self):
        """Test that all expected URL patterns exist."""
        expected_urls = [
            'users:login',
            'users:register',
            'users:account',
            'users:logout',
            'users:password_change',
            'users:forgot_password',
            'users:reset_password',
        ]

        for url_name in expected_urls:
            try:
                url = reverse(url_name)
                assert url is not None
            except Exception as e:
                pytest.fail(
                    f"URL pattern '{url_name}' not found: {e}"
                )

    @pytest.mark.url
    def test_url_resolution(self):
        """Test URL resolution for user patterns."""
        resolver = resolve('/users/login/')
        assert resolver.view_name == 'users:login'

        resolver = resolve('/users/register/')
        assert resolver.view_name == 'users:register'

        resolver = resolve('/users/account/')
        assert resolver.view_name == 'users:account'

        resolver = resolve('/users/logout/')
        assert resolver.view_name == 'users:logout'

        resolver = resolve('/users/password/change/')
        assert resolver.view_name == 'users:password_change'

        resolver = resolve('/users/forgot-password/')
        assert resolver.view_name == 'users:forgot_password'

        resolver = resolve('/users/reset-password/')
        assert resolver.view_name == 'users:reset_password'
