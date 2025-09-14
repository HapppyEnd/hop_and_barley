import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Category, Product

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for the entire test session."""
    with django_db_blocker.unblock():
        pass


@pytest.fixture
def api_client():
    """API client for testing API endpoints."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(user):
    """API client with authenticated user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_api_client(admin_user):
    """API client with authenticated admin user."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def request_factory():
    """Django request factory for testing views."""
    return RequestFactory()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def category():
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        description='Test product description',
        category=category,
        price=29.99,
        stock=100,
        is_active=True
    )


@pytest.fixture
def order(user):
    """Create a test order."""
    return Order.objects.create(
        user=user,
        status='pending',
        shipping_address='123 Test St, Test City, TC 12345'
    )


@pytest.fixture
def order_item(order, product):
    """Create a test order item."""
    return OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=product.price
    )


@pytest.fixture
def multiple_products(category):
    """Create multiple test products."""
    products = []
    for i in range(5):
        product = Product.objects.create(
            name=f'Test Product {i+1}',
            slug=f'test-product-{i+1}',
            description=f'Test product {i+1} description',
            category=category,
            price=19.99 + (i * 10),
            stock=50 + (i * 10),
            is_active=True
        )
        products.append(product)
    return products


@pytest.fixture
def multiple_categories():
    """Create multiple test categories."""
    categories = []
    for i in range(3):
        category = Category.objects.create(
            name=f'Test Category {i+1}',
            slug=f'test-category-{i+1}'
        )
        categories.append(category)
    return categories


@pytest.fixture
def sample_cart_data():
    """Sample cart data for testing."""
    return {
        '1': {'quantity': 2, 'price': '29.99'},
        '2': {'quantity': 1, 'price': '19.99'},
        '3': {'quantity': 3, 'price': '39.99'}
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        'shipping_address': '123 Test Street, Test City, TC 12345',
        'payment_method': 'card',
        'card_number': '4111111111111111',
        'card_expiry': '12/25',
        'card_cvv': '123',
        'card_holder': 'Test User'
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


@pytest.fixture
def mock_email_backend(django_settings):
    """Use file-based email backend for testing."""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    return settings


@pytest.fixture
def mock_media_root(django_settings, tmp_path):
    """Use temporary directory for media files during testing."""
    settings.MEDIA_ROOT = tmp_path
    return settings


@pytest.fixture
def mock_static_root(django_settings, tmp_path):
    """Use temporary directory for static files during testing."""
    settings.STATIC_ROOT = tmp_path
    return settings


# Pytest markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "model: mark test as model test"
    )
    config.addinivalue_line(
        "markers", "view: mark test as view test"
    )
    config.addinivalue_line(
        "markers", "form: mark test as form test"
    )
