import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.factories import (CategoryFactory, OrderFactory, OrderItemFactory,
                             ProductFactory, UserFactory)

User = get_user_model()


@pytest.mark.django_db
class TestCompleteUserJourney:
    """Integration tests for complete user journey."""

    @pytest.mark.integration
    def test_user_registration_to_order_completion(self, client):
        """Test complete flow from user registration to order completion."""
        registration_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

        response = client.post(
            reverse('users:register'), data=registration_data
        )
        assert response.status_code == 302

        user = User.objects.get(email='newuser@example.com')
        assert user.username == 'newuser'

        login_data = {
            'username': 'newuser@example.com',
            'password': 'testpass123'
        }

        response = client.post(reverse('users:login'), data=login_data)
        assert response.status_code == 302

        client.force_login(user)

        category = CategoryFactory(name='Test Category')
        products = ProductFactory.create_batch(3, category=category)

        response = client.get(reverse('products:product-list'))
        assert response.status_code == 200
        assert 'products' in response.context
        assert len(response.context['products']) == 3

        product = products[0]
        response = client.get(
            reverse('products:product-detail', args=[product.slug])
        )
        assert response.status_code == 200
        assert 'product' in response.context
        assert response.context['product'] == product

        response = client.post(
            reverse('orders:cart_add', args=[product.id]),
            {'quantity': 2, 'override': False}
        )
        assert response.status_code == 302

        response = client.get(reverse('orders:cart_detail'))
        assert response.status_code == 200
        assert 'cart' in response.context

        response = client.get(reverse('orders:checkout'))
        assert response.status_code == 200
        assert 'cart' in response.context

        order_data = {
            'shipping_address': (
                '123 Test St, Test City, TC 12345'
            ),
            'payment_method': 'card',
            'card_number': '4111111111111111',
            'expiry_date': '12/25',
            'cvv': '123',
            'card_holder': 'New User'
        }

        response = client.post(
            reverse('orders:checkout'), data=order_data
        )
        assert response.status_code == 302

        response = client.get(reverse('orders:order_list'))
        assert response.status_code == 200
        assert 'orders' in response.context
        assert len(response.context['orders']) == 1

        order = user.orders.first()
        response = client.get(
            reverse('orders:order_detail', args=[order.id])
        )
        assert response.status_code == 200
        assert 'order' in response.context
        assert response.context['order'] == order


@pytest.mark.django_db
class TestProductReviewWorkflow:
    """Integration tests for product review workflow."""

    @pytest.mark.integration
    def test_product_review_after_delivery(self, client):
        """Test product review workflow after order delivery."""
        user = UserFactory()
        product = ProductFactory()

        client.force_login(user)

        order = OrderFactory(user=user, status='delivered')
        OrderItemFactory(
            order=order, product=product, quantity=1, price=product.price
        )

        assert product.user_can_review(user)

        response = client.get(
            reverse('products:product-detail', args=[product.slug])
        )
        assert response.status_code == 200

        review_data = {
            'rating': 5,
            'title': 'Excellent product!',
            'comment': (
                'I love this product, highly recommended!'
            )
        }

        response = client.post(
            reverse('products:review-create', args=[product.slug]),
            data=review_data
        )
        assert response.status_code in [200, 302]

        review = product.reviews.filter(user=user).first()
        assert review is not None
        assert review.rating == 5
        assert review.title == 'Excellent product!'
        assert review.comment == 'I love this product, highly recommended!'

        from products.models import Review
        has_existing_review = Review.objects.filter(
            product=product, user=user
        ).exists()
        assert has_existing_review

        another_review_data = {
            'rating': 3,
            'title': 'Another review',
            'comment': 'This should not be allowed'
        }

        response = client.post(
            reverse('products:review-create', args=[product.slug]),
            data=another_review_data
        )
        assert response.status_code == 302

        review_count = Review.objects.filter(
            product=product, user=user
        ).count()
        assert review_count == 1

    @pytest.mark.integration
    def test_admin_review_creation(self, client):
        """Test admin can create reviews for any product."""
        admin = UserFactory(is_staff=True, is_superuser=True)
        product = ProductFactory()

        client.force_login(admin)

        assert product.user_can_review(admin)

        review_data = {
            'rating': 4,
            'title': 'Admin Review',
            'comment': 'This is an admin review.',
            'created_by_admin': True
        }

        response = client.post(
            reverse('products:review-create', args=[product.slug]),
            data=review_data
        )
        assert response.status_code in [200, 302]

        review = product.reviews.filter(user=admin).first()
        assert review is not None
        assert review.created_by_admin is True


@pytest.mark.django_db
class TestOrderManagementWorkflow:
    """Integration tests for order management workflow."""

    @pytest.mark.integration
    def test_order_status_update_workflow(self, client):
        """Test order status update workflow."""
        user = UserFactory()
        admin = UserFactory(is_staff=True, is_superuser=True)
        product = ProductFactory(stock=10)

        client.force_login(user)
        order = OrderFactory(user=user, status='pending')
        OrderItemFactory(
            order=order, product=product, quantity=2, price=product.price
        )

        client.force_login(admin)

        response = client.post(
            reverse('orders:update_order_status', args=[order.id]),
            {'status': 'placed'}
        )
        assert response.status_code in [200, 302]

        order.refresh_from_db()
        assert order.status == 'placed'

        response = client.post(
            reverse('orders:update_order_status', args=[order.id]),
            {'status': 'paid'}
        )
        assert response.status_code in [200, 302]

        order.refresh_from_db()
        assert order.status == 'paid'

        response = client.post(
            reverse('orders:update_order_status', args=[order.id]),
            {'status': 'shipped'}
        )
        assert response.status_code in [200, 302]

        order.refresh_from_db()
        assert order.status == 'shipped'

        response = client.post(
            reverse('orders:update_order_status', args=[order.id]),
            {'status': 'delivered'}
        )
        assert response.status_code in [200, 302]

        order.refresh_from_db()
        assert order.status == 'delivered'

    @pytest.mark.integration
    def test_order_cancellation_workflow(self, client):
        """Test order cancellation workflow."""
        user = UserFactory()
        product = ProductFactory(stock=10)

        client.force_login(user)

        order = OrderFactory(user=user, status='pending')
        OrderItemFactory(
            order=order, product=product, quantity=3, price=product.price
        )

        initial_stock = product.stock

        response = client.post(
            reverse('orders:cancel_order', args=[order.id])
        )
        assert response.status_code == 302

        order.refresh_from_db()
        assert order.status == 'canceled'

        product.refresh_from_db()
        assert product.stock == initial_stock + 3

    @pytest.mark.integration
    def test_order_cancellation_after_delivery_fails(self, client):
        """Test order cancellation fails after delivery."""
        user = UserFactory()
        product = ProductFactory()

        client.force_login(user)

        order = OrderFactory(user=user, status='delivered')
        OrderItemFactory(
            order=order, product=product, quantity=2, price=product.price
        )

        response = client.post(
            reverse('orders:cancel_order', args=[order.id])
        )
        assert response.status_code == 400

        order.refresh_from_db()
        assert order.status == 'delivered'
