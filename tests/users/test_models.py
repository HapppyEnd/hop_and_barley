import pytest
from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import PhoneNumber

from tests.factories import AdminUserFactory, UserFactory


@pytest.fixture
def user_model():
    """Get User model."""
    return get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for User model."""

    @pytest.mark.model
    def test_user_creation(self):
        """Test user creation with required fields."""
        user = UserFactory()
        assert user.email is not None
        assert user.username is not None
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.model
    def test_user_str_representation(self):
        """Test user string representation."""
        user = UserFactory(email='test@example.com')
        assert str(user) == 'test@example.com'

    @pytest.mark.model
    def test_user_full_name_property(self):
        """Test user full_name property."""
        user = UserFactory(first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'

        user = UserFactory(first_name='', last_name='')
        assert user.full_name == user.username

    @pytest.mark.model
    def test_user_email_uniqueness(self):
        """Test email uniqueness constraint."""
        UserFactory(email='test@example.com')
        with pytest.raises(Exception):
            UserFactory(email='test@example.com')

    @pytest.mark.model
    def test_user_phone_field(self):
        """Test phone number field."""
        user = UserFactory(phone='+1234567890')
        assert user.phone == PhoneNumber.from_string('+1234567890')

    @pytest.mark.model
    def test_user_optional_fields(self):
        """Test optional fields can be empty."""
        user = UserFactory(
            phone=None,
            city=None,
            address=None
        )
        assert user.phone is None
        assert user.city is None
        assert user.address is None
        assert user.image is not None
        assert user.image.name == 'profile_image/default.jpg'

    @pytest.mark.model
    def test_admin_user_creation(self):
        """Test admin user creation."""
        admin = AdminUserFactory()
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active
