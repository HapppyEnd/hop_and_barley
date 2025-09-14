from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Category, Product
from tests.factories import (CategoryFactory, MaltCategoryFactory,
                             ProductFactory, ReviewFactory, UserFactory)


@pytest.mark.django_db
class TestCategoryModel:
    """Test cases for Category model."""

    @pytest.mark.model
    def test_category_creation(self):
        """Test category creation with required fields."""
        category = CategoryFactory()
        assert category.name is not None
        assert category.slug is not None
        assert category.parent is None

    @pytest.mark.model
    def test_category_str_representation(self):
        """Test category string representation."""
        category = CategoryFactory(name='Test Category')
        assert str(category) == 'Test Category'

    @pytest.mark.model
    def test_category_slug_generation(self):
        """Test category slug generation."""
        category = Category(name='Test Category Name')
        category.save()
        assert category.slug == 'test-category-name'

    @pytest.mark.model
    def test_category_hierarchy(self):
        """Test category parent-child relationship."""
        parent = CategoryFactory(name='Parent Category')
        child = CategoryFactory(name='Child Category', parent=parent)

        assert child.parent == parent
        assert child in parent.subcategories.all()

    @pytest.mark.model
    def test_category_specifications(self):
        """Test category specifications method."""
        malt_category = MaltCategoryFactory()
        specs = malt_category.get_specifications()

        assert 'type' in specs
        assert 'usage' in specs
        assert 'recommended_styles' in specs
        assert specs['type'] == 'Specialty Malt'


@pytest.mark.django_db
class TestProductModel:
    """Test cases for Product model."""

    @pytest.mark.model
    def test_product_creation(self):
        """Test product creation with required fields."""
        product = ProductFactory()
        assert product.name is not None
        assert product.slug is not None
        assert product.description is not None
        assert product.category is not None
        assert product.price is not None
        assert product.stock is not None
        assert product.is_active is True

    @pytest.mark.model
    def test_product_str_representation(self):
        """Test product string representation."""
        product = ProductFactory(name='Test Product')
        assert str(product) == 'Test Product'

    @pytest.mark.model
    def test_product_slug_generation(self):
        """Test product slug generation."""
        category = CategoryFactory()
        product = Product(
            name='Test Product Name',
            description='Test description',
            category=category,
            price=Decimal('10.00'),
            stock=100
        )
        product.save()
        assert product.slug == 'test-product-name'

    @pytest.mark.model
    def test_product_get_image_url(self):
        """Test product image URL property."""
        product = ProductFactory()
        assert product.get_image_url == '/media/product_images/default.png'
        image_content = b'fake_image_content'
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            image_content,
            content_type='image/jpeg'
        )
        product.image = image_file
        product.save()

        assert 'test_image' in product.get_image_url

    @pytest.mark.model
    def test_product_user_can_review_authenticated(self):
        """Test user can review product when authenticated."""
        user = UserFactory()
        product = ProductFactory()

        assert not product.user_can_review(user)

    @pytest.mark.model
    def test_product_user_can_review_unauthenticated(self):
        """Test user cannot review product when not authenticated."""
        product = ProductFactory()

        assert not product.user_can_review(None)

    @pytest.mark.model
    def test_product_user_can_review_admin(self):
        """Test admin can review any product."""
        admin = UserFactory(is_staff=True)
        product = ProductFactory()

        assert product.user_can_review(admin)


@pytest.mark.django_db
class TestReviewModel:
    """Test cases for Review model."""

    @pytest.mark.model
    def test_review_creation(self):
        """Test review creation with required fields."""
        review = ReviewFactory()
        assert review.product is not None
        assert review.user is not None
        assert review.rating is not None
        assert review.comment is not None
        assert review.created_by_admin is False

    @pytest.mark.model
    def test_review_str_representation(self):
        """Test review string representation."""
        user = UserFactory(username='testuser')
        product = ProductFactory(name='Test Product')
        review = ReviewFactory(
            user=user,
            product=product,
            rating=5,
            comment='Great product!'
        )
        expected = 'testuser: 5 - Great product!'
        assert str(review) == expected

    @pytest.mark.model
    def test_review_rating_validation(self):
        """Test review rating validation."""
        review = ReviewFactory()

        for rating in [1, 2, 3, 4, 5]:
            review.rating = rating
            review.full_clean()
        for rating in [0, 6, -1]:
            review.rating = rating
            with pytest.raises(ValidationError):
                review.full_clean()

    @pytest.mark.model
    def test_review_unique_together(self):
        """Test review unique constraint on user and product."""
        user = UserFactory()
        product = ProductFactory()

        ReviewFactory(user=user, product=product)
        with pytest.raises(Exception):
            ReviewFactory(user=user, product=product)
