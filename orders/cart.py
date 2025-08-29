from django.conf import settings

from products.models import Product


class Cart:
    """Класс для управления корзиной через сессии."""

    def __init__(self, request):
        """Инициализация корзины."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        else:
            self._clean_cart_data(cart)
        self.cart = cart

    @staticmethod
    def _clean_cart_data(cart):
        """Очищает поврежденные данные в корзине."""
        items_to_remove = []
        for product_id, item in cart.items():
            try:
                required_keys = ['quantity', 'price', 'name', 'stock']
                if not all(key in item for key in required_keys):
                    items_to_remove.append(product_id)
                    continue
                int(item['quantity'])
                float(item['price'])
            except (ValueError, TypeError, KeyError):
                items_to_remove.append(product_id)
        for product_id in items_to_remove:
            del cart[product_id]

    def add(self, product, quantity=1, override_quantity=False):
        """Добавляет товар в корзину или обновляет его количество."""
        product_id = str(product.id)
        if product_id not in self.cart:
            try:
                price = float(product.price)
            except (ValueError, TypeError):
                price = 0.0
            self.cart[product_id] = {
                'quantity': quantity,
                'price': price,
                'name': product.name,
                'image': product.image.url if product.image else None,
                'stock': product.stock
            }
        else:
            if override_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock

        self.save()

    def save(self):
        """Помечает сессию как измененную."""
        self.session.modified = True

    def remove(self, product):
        """Удаляет товар из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Итерируется по товарам в корзине."""
        for product_id, item in self.cart.items():
            item_copy = item.copy()
            try:
                price = item_copy['price']
                quantity = item_copy['quantity']
                if isinstance(price, str):
                    price = float(price.replace('$', ''))
                else:
                    price = float(price)
                quantity = int(quantity)
                if price <= 0 or quantity <= 0:
                    continue
                item_copy['price'] = f"${price:.2f}"
                total_price = price * quantity
                item_copy['total_price'] = f"${total_price:.2f}"
                item_copy['product_id'] = product_id
                yield item_copy
            except (ValueError, TypeError):
                continue

    def __len__(self):
        """Возвращает общее количество товаров в корзине."""
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total_price(self):
        """Возвращает общую стоимость корзины."""
        total = 0

        for item in self.cart.values():
            try:
                price = item['price']
                quantity = item['quantity']
                if isinstance(price, str):
                    price = float(price.replace('$', ''))
                else:
                    price = float(price)
                quantity = int(quantity)
                if price > 0 and quantity > 0:
                    subtotal = price * quantity
                    total += subtotal
            except (ValueError, TypeError):
                continue
        return f"${total:.2f}"

    def clear(self):
        """Удаляет корзину из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_product_quantity(self, product_id):
        """Возвращает количество конкретного товара в корзине."""
        quantity = self.cart.get(str(product_id), {}).get('quantity', 0)
        return int(quantity) if quantity else 0

    def update_stock_info(self):
        """Обновляет информацию об остатках товаров."""
        for product_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                item['stock'] = product.stock
                if int(item['quantity']) > product.stock:
                    item['quantity'] = product.stock
            except Product.DoesNotExist:
                del self.cart[product_id]
        self.save()
