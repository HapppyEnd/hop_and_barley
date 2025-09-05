import random
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from orders.cart import Cart
from orders.mixins import OrderPermissionMixin
from orders.models import Order, OrderItem
from products.models import Product


def get_cart_response(cart, success=True, message="", total_price=None):
    """Create consistent cart responses."""
    response_data = {
        'success': success,
        'cart_count': len(cart),
    }

    if message:
        response_data['message'] = message
    if total_price is not None:
        response_data['total_price'] = str(total_price)

    return response_data


def handle_cart_operation(request, operation_func, success_message,
                          error_message="Invalid operation"):
    """Handle common cart operations with consistent responses."""
    cart = Cart(request)
    product_id = (request.POST.get('product_id') or
                  request.resolver_match.kwargs.get('product_id'))
    product = get_object_or_404(Product, id=product_id)

    try:
        operation_func(cart, product, request)
        messages.success(request, success_message)
        response_data = get_cart_response(cart, message=success_message)
    except Exception:
        messages.error(request, error_message)
        response_data = get_cart_response(cart, success=False,
                                          message=error_message)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(response_data)

    return redirect('orders:cart_detail')


def validate_quantity(quantity, product):
    """Validate quantity against product stock."""
    return 0 < quantity <= product.stock


def create_order_items_from_cart(order, cart):
    """Create order items from cart contents."""
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


def get_payment_display_name(payment_method):
    """Get display name for payment method."""
    return settings.PAYMENT_DISPLAY_NAMES.get(
        payment_method, 'Credit/Debit Card'
    )


def get_status_display_name(status):
    """Get display name for order status."""
    status_choices = dict(settings.ORDER_STATUS_CHOICES)
    return status_choices.get(status, status)


def cart_detail(request):
    """Display cart page."""
    cart = Cart(request)
    cart.update_stock_info()

    return render(request, 'orders/cart.html', {
        'cart': cart
    })


@require_POST
def cart_add(request, product_id):
    """Add product to cart."""

    def add_operation(cart, product, request):
        quantity = int(request.POST.get('quantity', 1))
        if not validate_quantity(quantity, product):
            raise ValueError('Invalid quantity')
        cart.add(product=product, quantity=quantity)

    return handle_cart_operation(
        request,
        add_operation,
        f'"{Product.objects.get(id=product_id).name}" added to cart',
        'Invalid quantity'
    )


@require_POST
def cart_remove(request, product_id):
    """Remove product from cart."""

    def remove_operation(cart, product, request):
        cart.remove(product)

    return handle_cart_operation(
        request,
        remove_operation,
        f'"{Product.objects.get(id=product_id).name}" removed from cart'
    )


@require_POST
def cart_update(request, product_id):
    """Update product quantity in cart."""

    def update_operation(cart, product, request):
        quantity = int(request.POST.get('quantity', 1))
        if not validate_quantity(quantity, product):
            raise ValueError('Invalid quantity')
        cart.add(product=product, quantity=quantity, override_quantity=True)

    cart = Cart(request)
    response = handle_cart_operation(
        request,
        update_operation,
        f'Quantity of "{Product.objects.get(id=product_id).name}" updated',
        'Invalid quantity'
    )

    if isinstance(response, JsonResponse):
        response_data = get_cart_response(cart,
                                          total_price=cart.get_total_price())
        return JsonResponse(response_data)

    return response


@login_required
def checkout(request):
    """Process order checkout."""
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, settings.ORDER_MESSAGES['CART_EMPTY'])
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method', 'card')

        if not shipping_address:
            messages.error(
                request, settings.ORDER_MESSAGES['SHIPPING_ADDRESS_REQUIRED']
            )
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'user': request.user
            })

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address
        )

        try:
            create_order_items_from_cart(order, cart)

            card_details = get_card_details(request, payment_method)
            payment_success = process_payment(payment_method, order,
                                              card_details)

            if payment_success:
                order.status = (
                    settings.ORDER_STATUS_PLACED
                    if payment_method == 'cash_on_delivery'
                    else settings.ORDER_STATUS_PAID
                )
                order.save()

                success_msg = get_checkout_success_message(payment_method)
                messages.success(request, success_msg)

                order.reduce_stock()
                cart.clear()
                send_order_notifications(order, payment_method)

                return redirect('orders:order_detail', order_id=order.id)
            else:
                order.delete()
                messages.error(
                    request, settings.ORDER_MESSAGES['PAYMENT_FAILED']
                )
        except Exception as e:
            order.delete()
            messages.error(
                request,
                settings.ORDER_MESSAGES['ORDER_ERROR'].format(error=e)
            )

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'user': request.user
    })


def get_card_details(request, payment_method):
    """Extract card details from request."""
    if payment_method == 'card':
        return {
            'card_number': request.POST.get('card_number', ''),
            'card_holder': request.POST.get('card_holder', ''),
            'expiry_date': request.POST.get('expiry_date', ''),
            'cvv': request.POST.get('cvv', ''),
        }
    return None


def get_checkout_success_message(payment_method):
    """Get success message based on payment method."""
    if payment_method == 'cash_on_delivery':
        return settings.ORDER_MESSAGES['ORDER_CONFIRMATION_COD']
    else:
        return settings.ORDER_MESSAGES['ORDER_CONFIRMATION_PAID']


@login_required
def order_detail(request, order_id):
    """Display order details."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


@login_required
def order_list(request):
    """Display user order list."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })


@login_required
def update_order_status(request, order_id):
    """Update order status."""
    order = get_object_or_404(Order, id=order_id)

    if not OrderPermissionMixin.check_order_permission(
            request, request.user, order,
            'You do not have permission to update this order.'):
        return redirect('orders:order_detail', order_id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(settings.ORDER_STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()

            send_status_change_notification(order, old_status, new_status)

            status_display = order.get_status_display()
            success_msg = settings.ORDER_MESSAGES[
                'ORDER_STATUS_UPDATED'
            ].format(status=status_display)
            messages.success(request, success_msg)
        else:
            messages.error(request, settings.ORDER_MESSAGES['INVALID_STATUS'])

    return redirect('orders:order_detail', order_id=order_id)


@login_required
def cancel_order(request, order_id):
    """Cancel order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_canceled():
        messages.error(
            request, settings.ORDER_MESSAGES['ORDER_CANNOT_BE_CANCELED']
        )
        return redirect('orders:order_detail', order_id=order_id)

    if request.method == 'POST':
        try:
            old_status = order.status
            order.cancel_order()

            send_status_change_notification(
                order, old_status, settings.ORDER_STATUS_CANCELED)

            messages.success(
                request, settings.ORDER_MESSAGES['ORDER_CANCELED_SUCCESS']
            )
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('orders:order_detail', order_id=order_id)


def process_payment(payment_method, order, card_details=None):
    """Process payment."""
    success_rates = {
        'card': 0.95,
        'cash_on_delivery': 1.0,
    }

    success_rate = success_rates.get(payment_method, 0.95)

    if payment_method == 'card' and card_details:
        card_number = card_details.get('card_number', '').replace(' ', '')
        card_holder = card_details.get('card_holder', '').strip()
        expiry_date = card_details.get('expiry_date', '').strip()
        cvv = card_details.get('cvv', '').strip()

        if not card_number or len(card_number) < 13:
            return False
        if not card_holder or len(card_holder) < 2:
            return False
        if not expiry_date or not expiry_date.count('/') == 1:
            return False
        if not cvv or len(cvv) < 3:
            return False

        if card_number.startswith('4000'):
            return False
    return random.random() < success_rate


def send_order_notifications(order, payment_method):
    """Send order email notifications."""
    payment_display = get_payment_display_name(payment_method)
    user_name = order.user.get_full_name() or order.user.username

    send_customer_order_notification(order, user_name, payment_display)

    send_admin_order_notification(order, user_name, payment_display)


def send_customer_order_notification(order, user_name, payment_display):
    """Send order confirmation email to customer."""
    from django.conf import settings

    customer_subject = f'Order Confirmation #{order.id} - Hop & Barley'
    customer_html = render_to_string('orders/emails/order_confirmation.html', {
        'order': order,
        'user_name': user_name,
        'payment_display': payment_display,
    })

    customer_text = build_customer_email_text(order, user_name,
                                              payment_display)

    send_mail(
        customer_subject,
        customer_text,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=customer_html,
        fail_silently=False
    )


def send_admin_order_notification(order, user_name, payment_display):
    """Send order notification to admin."""
    from django.conf import settings

    admin_subject = f'New Order #{order.id} - {user_name}'
    admin_message = build_admin_email_text(order, user_name, payment_display)

    admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
    send_mail(
        admin_subject,
        admin_message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False
    )


def build_customer_email_text(order, user_name, payment_display):
    """Build customer email text content."""
    items_text = build_items_text(order)

    return f"""
Dear {user_name},

Thank you for your order! We've received your order and are processing it.

Order Details:
- Order Number: #{order.id}
- Order Date: {order.created_at.strftime('%B %d, %Y')}
- Status: {order.get_status_display()}
- Payment Method: {payment_display}

Items Ordered:
{items_text}

Total: {order.total_price}

Shipping Address:
{order.shipping_address}

We'll send you another email when your order ships.
If you have any questions, please don't hesitate to contact us.

Best regards,
The Hop & Barley Team

© 2025 Hop & Barley. All rights reserved.
"""


def build_admin_email_text(order, user_name, payment_display):
    """Build admin email text content."""
    items_text = build_items_text(order)

    return f"""
New Order Alert!

A new order has been placed and requires your attention.

Customer Information:
- Name: {user_name}
- Email: {order.user.email}
- Order Date: {order.created_at.strftime('%B %d, %Y %H:%M')}
- Payment Method: {payment_display}

Order Details:
- Order Number: #{order.id}
- Status: {order.get_status_display()}

Items Ordered:
{items_text}

Total: {order.total_price}

Shipping Address:
{order.shipping_address}

Action Required: Please process this order and update the status accordingly.
"""


def build_items_text(order):
    """Build items text for email content."""
    items_text = ""
    for item in order.items.all():
        items_text += (
            f"- {item.product.name} × {item.quantity} - {item.total}\n"
        )
    return items_text


def send_status_change_notification(order, old_status, new_status):
    """Send order status change notification."""
    from django.conf import settings

    old_status_display = get_status_display_name(old_status)
    new_status_display = get_status_display_name(new_status)
    user_name = order.user.get_full_name() or order.user.username

    customer_subject = f'Order Status Update #{order.id} - Hop & Barley'
    customer_html = render_to_string(
        'orders/emails/order_status_update.html', {
            'order': order,
            'user_name': user_name,
            'old_status_display': old_status_display,
            'new_status_display': new_status_display,
            'new_status': new_status,
        })

    customer_text = build_status_change_email_text(
        order, user_name, old_status_display, new_status_display, new_status
    )

    send_mail(
        customer_subject,
        customer_text,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=customer_html,
        fail_silently=False
    )


def build_status_change_email_text(order, user_name, old_status_display,
                                   new_status_display, new_status):
    """Build status change email text content."""
    items_text = build_items_text(order)
    status_message = get_status_change_message(new_status)

    return f"""
Dear {user_name},

Your order status has been updated.

Order Details:
- Order Number: #{order.id}
- Previous Status: {old_status_display}
- New Status: {new_status_display}
- Updated Date: {order.updated_at.strftime('%B %d, %Y %H:%M')}

Items Ordered:
{items_text}

Total: {order.total_price}

Shipping Address:
{order.shipping_address}

{status_message}

If you have any questions, please don't hesitate to contact us.

Best regards,
The Hop & Barley Team

© 2025 Hop & Barley. All rights reserved.
"""


def get_status_change_message(new_status):
    """Get message based on new status."""
    return settings.STATUS_CHANGE_MESSAGES.get(new_status, "")
