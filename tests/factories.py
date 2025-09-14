import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()


def get_user_model():
    """Get User model when needed."""
    from django.contrib.auth import get_user_model
    return get_user_model()


def get_category_model():
    """Get Category model when needed."""
    from products.models import Category
    return Category


def get_product_model():
    """Get Product model when needed."""
    from products.models import Product
    return Product


def get_review_model():
    """Get Review model when needed."""
    from products.models import Review
    return Review


def get_order_model():
    """Get Order model when needed."""
    from orders.models import Order
    return Order


def get_order_item_model():
    """Get OrderItem model when needed."""
    from orders.models import OrderItem
    return OrderItem


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = 'users.User'

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Faker('phone_number')
    city = factory.Faker('city')
    address = factory.Faker('address')
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class AdminUserFactory(DjangoModelFactory):
    """Factory for creating admin users."""

    class Meta:
        model = 'users.User'

    username = factory.Sequence(lambda n: f'admin{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Faker('phone_number')
    city = factory.Faker('city')
    address = factory.Faker('address')
    is_active = True
    is_staff = True
    is_superuser = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'adminpass123'
        self.set_password(password)
        self.save()


class CategoryFactory(DjangoModelFactory):
    """Factory for creating test categories."""

    class Meta:
        model = 'products.Category'

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{n}')
    parent = None


class ProductFactory(DjangoModelFactory):
    """Factory for creating test products."""

    class Meta:
        model = 'products.Product'

    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.Sequence(lambda n: f'product-{n}')
    description = factory.Faker('text', max_nb_chars=200)
    category = factory.SubFactory(CategoryFactory)
    price = factory.Faker(
        'pydecimal', left_digits=3, right_digits=2, positive=True
    )
    stock = factory.Faker('random_int', min=0, max=1000)
    is_active = True


class ReviewFactory(DjangoModelFactory):
    """Factory for creating test reviews."""

    class Meta:
        model = 'products.Review'

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    title = factory.Faker('sentence', nb_words=3)
    comment = factory.Faker('text', max_nb_chars=500)
    created_by_admin = False


class OrderFactory(DjangoModelFactory):
    """Factory for creating test orders."""

    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    status = factory.Iterator([
        'pending', 'placed', 'paid', 'shipped', 'delivered', 'canceled'
    ])
    shipping_address = factory.Faker('address')


class OrderItemFactory(DjangoModelFactory):
    """Factory for creating test order items."""

    class Meta:
        model = 'orders.OrderItem'

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_int', min=1, max=10)
    price = factory.LazyAttribute(
        lambda obj: obj.product.price if obj.product else 0
    )


class DeliveredOrderFactory(DjangoModelFactory):
    """Factory for creating delivered orders."""

    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    status = 'delivered'
    shipping_address = factory.Faker('address')


class PendingOrderFactory(DjangoModelFactory):
    """Factory for creating pending orders."""

    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    status = 'pending'
    shipping_address = factory.Faker('address')


class PaidOrderFactory(DjangoModelFactory):
    """Factory for creating paid orders."""

    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    status = 'paid'
    shipping_address = factory.Faker('address')


class CanceledOrderFactory(DjangoModelFactory):
    """Factory for creating canceled orders."""

    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    status = 'canceled'
    shipping_address = factory.Faker('address')


class MaltCategoryFactory(DjangoModelFactory):
    """Factory for creating malt categories."""

    class Meta:
        model = 'products.Category'

    name = 'Malt'
    slug = 'malt'
    parent = None


class HopsCategoryFactory(DjangoModelFactory):
    """Factory for creating hops categories."""

    class Meta:
        model = 'products.Category'

    name = 'Hops'
    slug = 'hops'
    parent = None


class EquipmentCategoryFactory(DjangoModelFactory):
    """Factory for creating equipment categories."""

    class Meta:
        model = 'products.Category'

    name = 'Equipment'
    slug = 'equipment'
    parent = None


class MaltProductFactory(DjangoModelFactory):
    """Factory for creating malt products."""

    class Meta:
        model = 'products.Product'

    name = factory.Iterator([
        'Maris Otter Malt',
        'Caramel Malt',
        'Chocolate Malt',
        'Munich Malt'
    ])
    slug = factory.LazyAttribute(
        lambda obj: obj.name.lower().replace(' ', '-')
    )
    description = factory.Faker('text', max_nb_chars=200)
    category = factory.SubFactory(MaltCategoryFactory)
    price = factory.Faker(
        'pydecimal', left_digits=3, right_digits=2, positive=True
    )
    stock = factory.Faker('random_int', min=0, max=1000)
    is_active = True


class HopsProductFactory(DjangoModelFactory):
    """Factory for creating hops products."""

    class Meta:
        model = 'products.Product'

    name = factory.Iterator([
        'Cascade Hops',
        'Centennial Hops',
        'Citra Hops',
        'Mosaic Hops'
    ])
    slug = factory.LazyAttribute(
        lambda obj: obj.name.lower().replace(' ', '-')
    )
    description = factory.Faker('text', max_nb_chars=200)
    category = factory.SubFactory(HopsCategoryFactory)
    price = factory.Faker(
        'pydecimal', left_digits=3, right_digits=2, positive=True
    )
    stock = factory.Faker('random_int', min=0, max=1000)
    is_active = True


class EquipmentProductFactory(DjangoModelFactory):
    """Factory for creating equipment products."""

    class Meta:
        model = 'products.Product'

    name = factory.Iterator([
        'Brewing Kettle',
        'Fermentation Vessel',
        'Hydrometer',
        'Thermometer'
    ])
    slug = factory.LazyAttribute(
        lambda obj: obj.name.lower().replace(' ', '-')
    )
    description = factory.Faker('text', max_nb_chars=200)
    category = factory.SubFactory(EquipmentCategoryFactory)
    price = factory.Faker(
        'pydecimal', left_digits=3, right_digits=2, positive=True
    )
    stock = factory.Faker('random_int', min=0, max=1000)
    is_active = True
