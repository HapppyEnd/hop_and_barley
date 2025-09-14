from django.http import HttpRequest, HttpResponse

from orders.cart import Cart


def _mock_get_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


def create_mock_request():
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get('/')
    middleware = SessionMiddleware(_mock_get_response)
    middleware.process_request(request)
    request.session.save()
    return request


class TestCartFunctionality:

    def test_cart_initialization(self, client):
        """Test cart initialization."""
        request = create_mock_request()
        cart = Cart(request)
        assert len(cart) == 0
        assert cart.get_total_price() == "$0.00"

    def test_cart_add_item(self, product):
        """Test adding item to cart."""
        request = create_mock_request()
        cart = Cart(request)
        quantity = 2
        cart.add(product, quantity)
        assert len(cart) == quantity
        assert cart.cart[str(product.id)]['quantity'] == quantity
        assert cart.cart[str(product.id)]['price'] == float(product.price)

    def test_cart_add_existing_item(self, product):
        """Test adding existing item to cart updates quantity."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        cart.add(product, 3)
        assert len(cart) == 5
        assert cart.cart[str(product.id)]['quantity'] == 5

    def test_cart_remove_item(self, product):
        """Test removing item from cart."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        assert len(cart) == 2
        cart.remove(product)
        assert len(cart) == 0
        assert str(product.id) not in cart.cart

    def test_cart_clear(self, product):
        """Test clearing cart."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        assert len(cart) == 2
        cart.clear()
        assert len(cart) == 0

    def test_cart_get_total_price(self, product):
        """Test cart total price calculation."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        expected_total = 2 * float(product.price)
        assert cart.get_total_price() == f"${expected_total:.2f}"

    def test_cart_iteration(self, product):
        """Test cart iteration."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        items = list(cart)
        assert len(items) == 1
        assert items[0]['product_id'] == str(product.id)

    def test_cart_update_quantity(self, product):
        """Test updating item quantity in cart."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        cart.add(product, 1, override_quantity=True)
        assert cart.cart[str(product.id)]['quantity'] == 1

    def test_cart_add_with_override_false(self, product):
        """Test adding item with override=False (default behavior)."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        cart.add(product, 3, override_quantity=False)
        assert cart.cart[str(product.id)]['quantity'] == 5

    def test_cart_add_with_override_true(self, product):
        """Test adding item with override=True."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        cart.add(product, 3, override_quantity=True)
        assert cart.cart[str(product.id)]['quantity'] == 3

    def test_cart_empty_after_clear(self, product):
        """Test cart is empty after clearing."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        assert len(cart) == 2
        cart.clear()
        assert len(cart) == 0
        assert cart.get_total_price() == "$0.00"

    def test_cart_remove_nonexistent_item(self, product):
        """Test removing non-existent item from cart."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 2)
        assert len(cart) == 2
        from tests.factories import ProductFactory
        other_product = ProductFactory()
        cart.remove(other_product)
        assert len(cart) == 2
        assert str(product.id) in cart.cart

    def test_cart_with_zero_quantity(self, product):
        """Test cart behavior with zero quantity."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, 0)
        assert len(cart) == 0
        assert str(product.id) not in cart.cart

    def test_cart_with_negative_quantity(self, product):
        """Test cart behavior with negative quantity."""
        request = create_mock_request()
        cart = Cart(request)
        cart.add(product, -1)
        assert len(cart) == 0
        assert str(product.id) not in cart.cart
