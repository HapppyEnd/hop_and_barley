from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .models import Order, OrderItem


def cart_detail(request):
    """Display cart."""
    cart = Cart(request)
    cart.update_stock_info()

    return render(request, 'orders/cart.html', {
        'cart': cart
    })


@require_POST
def cart_add(request, product_id):
    """Add product to cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))

    if 0 < quantity <= product.stock:
        cart.add(product=product, quantity=quantity)
        messages.success(
            request,
            f'"{product.name}" added to cart')
    else:
        messages.error(request, 'Invalid quantity')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'message': f'"{product.name}" added to cart'
        })

    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Remove product from cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'"{product.name}" removed from cart')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'message': f'"{product.name}" removed from cart'
        })

    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if 0 < quantity <= product.stock:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f'Quantity of "{product.name}" updated')
    else:
        messages.error(request, 'Invalid quantity')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'total_price': str(cart.get_total_price())
        })

    return redirect('orders:cart_detail')


@login_required
def checkout(request):
    """Checkout order."""
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')

        if shipping_address:
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address
            )

            for item in cart:
                product = Product.objects.get(id=item['product_id'])
                price_str = item['price'].replace('$', '').strip()
                price = Decimal(price_str)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=price
                )

            try:
                order.reduce_stock()
                cart.clear()
                messages.success(request, 'Order successfully placed!')
                return redirect('orders:order_detail', order_id=order.id)
            except Exception as e:
                order.delete()
                messages.error(request, f'Error placing order: {e}')
        else:
            messages.error(request, 'Please provide shipping address')

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'user': request.user
    })


@login_required
def order_detail(request, order_id):
    """Order details."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


@login_required
def order_list(request):
    """User order list."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })
