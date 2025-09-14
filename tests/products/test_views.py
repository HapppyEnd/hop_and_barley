import pytest
from django.urls import reverse

from tests.factories import (HopsCategoryFactory, MaltCategoryFactory,
                             ProductFactory, ReviewFactory)


@pytest.mark.django_db
class TestProductViews:
    """Test cases for product views."""

    @pytest.mark.view
    def test_product_list_view(self, client):
        """Test product list view."""
        ProductFactory.create_batch(5)

        response = client.get(reverse('products:product-list'))
        assert response.status_code == 200
        assert 'products' in response.context
        assert len(response.context['products']) == 5

    @pytest.mark.view
    def test_product_detail_view(self, client):
        """Test product detail view."""
        product = ProductFactory()

        response = client.get(
            reverse('products:product-detail', args=[product.slug])
        )
        assert response.status_code == 200
        assert 'product' in response.context
        assert response.context['product'] == product

    @pytest.mark.view
    def test_product_detail_view_not_found(self, client):
        """Test product detail view with non-existent product."""
        response = client.get(
            reverse('products:product-detail', args=['non-existent'])
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestProductFiltering:
    """Test cases for product filtering functionality."""

    @pytest.mark.view
    def test_product_filter_by_category(self, client):
        """Test product filtering by category."""
        malt_category = MaltCategoryFactory()
        hops_category = HopsCategoryFactory()

        ProductFactory.create_batch(2, category=malt_category)
        ProductFactory.create_batch(3, category=hops_category)

        response = client.get(
            reverse('products:product-list'),
            {'category': malt_category.id}
        )
        assert response.status_code == 200
        assert 'products' in response.context
        assert len(response.context['products']) == 2

    @pytest.mark.view
    def test_product_filter_by_availability(self, client):
        """Test product filtering by availability."""
        ProductFactory.create_batch(2, is_active=True)
        ProductFactory.create_batch(3, is_active=False)

        response = client.get(
            reverse('products:product-list'), {'available': 'true'}
        )
        assert response.status_code == 200
        assert 'products' in response.context
        assert len(response.context['products']) == 2


@pytest.mark.django_db
class TestProductReviews:
    """Test cases for product reviews functionality."""

    @pytest.mark.view
    def test_review_form_display(self, client, user):
        """Test review form display for authenticated user."""
        product = ProductFactory()
        client.force_login(user)

        response = client.get(
            reverse('products:product-detail', args=[product.slug])
        )
        assert response.status_code == 200

    @pytest.mark.view
    def test_review_submission(self, client, user):
        """Test review submission."""
        product = ProductFactory()
        client.force_login(user)

        review_data = {
            'rating': 5,
            'title': 'Great product!',
            'comment': 'I love this product, highly recommended!'
        }

        response = client.post(
            reverse('products:review-create', args=[product.slug]),
            data=review_data
        )
        assert response.status_code in [200, 302]

    @pytest.mark.view
    def test_review_display(self, client):
        """Test review display on product page."""
        product = ProductFactory()
        ReviewFactory.create_batch(3, product=product)

        response = client.get(
            reverse('products:product-detail', args=[product.slug])
        )
        assert response.status_code == 200
        assert 'reviews' in response.context
        assert len(response.context['reviews']) == 3


@pytest.mark.django_db
class TestProductPagination:
    """Test cases for product pagination."""

    @pytest.mark.view
    def test_product_pagination(self, client):
        """Test product list pagination."""
        ProductFactory.create_batch(25)

        response = client.get(reverse('products:product-list'))
        assert response.status_code == 200
        assert 'is_paginated' in response.context
        assert 'page_obj' in response.context

    @pytest.mark.view
    def test_product_pagination_page_2(self, client):
        """Test product list pagination page 2."""
        ProductFactory.create_batch(25)

        response = client.get(
            reverse('products:product-list'), {'page': 2}
        )
        assert response.status_code == 200
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 2
