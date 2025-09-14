import random
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from orders.cart import Cart
from orders.mixins import OrderPermissionMixin
from orders.models import Order, OrderItem
from products.models import Product


def get_cart_response(
    cart: Cart,
    success: bool = True,
    message: str = "",
    total_price: Decimal | None = None
) -> dict[str, any]:
    """Create consistent cart responses.

    Args:
        cart: Cart instance
        success: Whether the operation was successful
        message: Optional success/error message
        total_price: Optional total price to include in response

    Returns:
        Dictionary with cart response data
    """
    response_data = {
        'success': success,
        'cart_count': len(cart),
    }

    if message:
        response_data['message'] = message
    if total_price is not None:
        response_data['total_price'] = str(total_price)

    return response_data


def handle_cart_operation(
    request: HttpRequest,
    operation_func: callable,
    success_message: str,
    error_message: str = "Invalid operation"
) -> JsonResponse | HttpResponse:
    """Handle common cart operations with consistent responses.

    Args:
        request: HTTP request object
        operation_func: Function to execute the cart operation
        success_message: Message to show on success
        error_message: Message to show on error

    Returns:
        JsonResponse for AJAX requests, HttpResponse redirect otherwise
    """
    cart = Cart(request)
    product_id = (request.POST.get('product_id') or
                  request.resolver_match.kwargs.get('product_id'))
    product = get_object_or_404(Product, id=product_id)

    try:
        operation_func(cart, product, request)
        messages.success(request, success_message)
        response_data = get_cart_response(cart, message=success_message)
    except (ValueError, TypeError, ValidationError):
        messages.error(request, error_message)
        response_data = get_cart_response(cart, success=False,
                                          message=error_message)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(response_data)

    return redirect('orders:cart_detail')


def validate_quantity(quantity: int, product: Product) -> bool:
    """Validate quantity against product stock."""
    return 0 < quantity <= product.stock


def create_order_items_from_cart(order: Order, cart: Cart) -> None:
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


def get_payment_display_name(payment_method: str) -> str:
    """Get display name for payment method."""
    return settings.PAYMENT_DISPLAY_NAMES.get(
        payment_method, 'Credit/Debit Card'
    )


def get_status_display_name(status: str) -> str:
    """Get display name for order status."""
    status_choices = dict(settings.ORDER_STATUS_CHOICES)
    return status_choices.get(status, status)


def cart_detail(request: HttpRequest) -> HttpResponse:
    """Display cart page."""
    cart = Cart(request)
    cart.update_stock_info()

    return render(request, 'orders/cart.html', {
        'cart': cart
    })


@require_POST
def cart_add(
    request: HttpRequest, product_id: int
) -> JsonResponse | HttpResponse:
    """Add product to cart.

    Args:
        request: HTTP request object
        product_id: ID of the product to add

    Returns:
        JsonResponse for AJAX requests, HttpResponse redirect otherwise
    """

    def add_operation(
        cart: Cart, product: Product, request: HttpRequest
    ) -> None:
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
def cart_remove(
    request: HttpRequest, product_id: int
) -> JsonResponse | HttpResponse:
    """Remove product from cart.

    Args:
        request: HTTP request object
        product_id: ID of the product to remove

    Returns:
        JsonResponse for AJAX requests, HttpResponse redirect otherwise
    """

    def remove_operation(
        cart: Cart, product: Product, request: HttpRequest
    ) -> None:
        cart.remove(product)

    return handle_cart_operation(
        request,
        remove_operation,
        f'"{Product.objects.get(id=product_id).name}" removed from cart'
    )


@require_POST
def cart_update(
    request: HttpRequest, product_id: int
) -> JsonResponse | HttpResponse:
    """Update product quantity in cart.

    Args:
        request: HTTP request object
        product_id: ID of the product to update

    Returns:
        JsonResponse for AJAX requests, HttpResponse redirect otherwise
    """

    def update_operation(
        cart: Cart, product: Product, request: HttpRequest
    ) -> None:
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
def checkout(request: HttpRequest) -> HttpResponse:
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

            if payment_method == 'card' and card_details:
                expiry_date = card_details.get('expiry_date', '').strip()
                if expiry_date and not validate_card_expiry(expiry_date):
                    order.delete()
                    messages.error(
                        request, settings.ORDER_MESSAGES['CARD_EXPIRED']
                    )
                    return render(request, 'orders/checkout.html', {
                        'cart': cart,
                        'user': request.user
                    })
            payment_success = process_payment(
                payment_method, order, card_details
            )

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
        except (ValidationError, ValueError, TypeError, AttributeError) as e:
            order.delete()
            messages.error(
                request,
                settings.ORDER_MESSAGES['ORDER_ERROR'].format(error=e)
            )

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'user': request.user
    })


def validate_card_expiry(expiry_date: str) -> bool:
    """Validate that the card is not expired."""
    try:
        month, year = expiry_date.split('/')
        month = int(month)
        year = int('20' + year)

        now = datetime.now()
        card_date = datetime(year, month, 1)
        current_date = datetime(now.year, now.month, 1)

        return card_date >= current_date
    except (ValueError, TypeError, IndexError):
        return False


def get_card_details(
    request: HttpRequest, payment_method: str
) -> dict[str, str] | None:
    """Extract card details from request.

    Args:
        request: HTTP request object
        payment_method: Payment method used

    Returns:
        Dictionary containing card details if payment method is 'card',
        None otherwise
    """
    if payment_method == 'card':
        return {
            'card_number': request.POST.get('card_number', ''),
            'card_holder': request.POST.get('card_holder', ''),
            'expiry_date': request.POST.get('expiry_date', ''),
            'cvv': request.POST.get('cvv', ''),
        }
    return None


def get_checkout_success_message(payment_method: str) -> str:
    """Get success message based on payment method."""
    if payment_method == 'cash_on_delivery':
        return settings.ORDER_MESSAGES['ORDER_CONFIRMATION_COD']
    else:
        return settings.ORDER_MESSAGES['ORDER_CONFIRMATION_PAID']


@login_required
def order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    """Display order details."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


@login_required
def order_list(request: HttpRequest) -> HttpResponse:
    """Display user order list."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })


@login_required
def update_order_status(request: HttpRequest, order_id: int) -> HttpResponse:
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
def cancel_order(request: HttpRequest, order_id: int) -> HttpResponse:
    """Cancel order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_canceled():
        messages.error(
            request, settings.ORDER_MESSAGES['ORDER_CANNOT_BE_CANCELED']
        )
        return render(request, 'orders/order_detail.html', {
            'order': order
        }, status=400)

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


def process_payment(
    payment_method: str,
    order: Order,
    card_details: dict[str, str] | None = None
) -> bool:
    """Process payment.

    Args:
        payment_method: Payment method used
        order: Order instance to process payment for
        card_details: Optional card details for card payments

    Returns:
        True if payment was successful, False otherwise
    """
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
        if not expiry_date or len(expiry_date) != 5:
            return False
        if not cvv or len(cvv) < 3:
            return False

        if not validate_card_expiry(expiry_date):
            return False

        if card_number.startswith('4000'):
            return False
    return random.random() < success_rate


def send_order_notifications(order: Order, payment_method: str) -> None:
    """Send order email notifications."""
    payment_display = get_payment_display_name(payment_method)
    user_name = order.user.get_full_name() or order.user.username

    send_customer_order_notification(order, user_name, payment_display)

    send_admin_order_notification(order, user_name, payment_display)


def send_customer_order_notification(
    order: Order, user_name: str, payment_display: str
) -> None:
    """Send order confirmation email to customer.

    Args:
        order: Order instance to send confirmation for
        user_name: Name of the user
        payment_display: Display name for payment method
    """
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


def send_admin_order_notification(
    order: Order, user_name: str, payment_display: str
) -> None:
    """Send order notification to admin.

    Args:
        order: Order instance to send notification for
        user_name: Name of the user
        payment_display: Display name for payment method
    """
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


def build_customer_email_text(
    order: Order, user_name: str, payment_display: str
) -> str:
    """Build customer email text content.

    Args:
        order: Order instance to build email for
        user_name: Name of the user
        payment_display: Display name for payment method

    Returns:
        Formatted email text content
    """
    items_text = build_items_text(order)
    email_templates = settings.EMAIL_TEMPLATES

    return f"""
{email_templates['CUSTOMER_GREETING'].format(user_name=user_name)}

{email_templates['CUSTOMER_THANK_YOU']}

{email_templates['ORDER_DETAILS_HEADER']}
- {email_templates['ORDER_NUMBER'].format(order_id=order.id)}
- {email_templates['ORDER_DATE'].format(
        date=order.created_at.strftime('%B %d, %Y')
    )}
- {email_templates['ORDER_STATUS'].format(status=order.get_status_display())}
- {email_templates['PAYMENT_METHOD'].format(payment=payment_display)}

{email_templates['ITEMS_ORDERED_HEADER']}
{items_text}

{email_templates['TOTAL_HEADER'].format(total=order.total_price)}

{email_templates['SHIPPING_ADDRESS_HEADER']}
{order.shipping_address}

{email_templates['CUSTOMER_FOOTER']}

{email_templates['BEST_REGARDS']}
{email_templates['TEAM_SIGNATURE']}

{email_templates['COPYRIGHT']}
"""


def build_admin_email_text(
    order: Order, user_name: str, payment_display: str
) -> str:
    """Build admin email text content.

    Args:
        order: Order instance to build email for
        user_name: Name of the user
        payment_display: Display name for payment method

    Returns:
        Formatted admin email text content
    """
    items_text = build_items_text(order)
    email_templates = settings.EMAIL_TEMPLATES

    return f"""
{email_templates['ADMIN_ALERT_HEADER']}

{email_templates['ADMIN_ALERT_MESSAGE']}

{email_templates['CUSTOMER_INFO_HEADER']}
- {email_templates['CUSTOMER_NAME'].format(name=user_name)}
- {email_templates['CUSTOMER_EMAIL'].format(email=order.user.email)}
- {email_templates['ORDER_DATE_TIME'].format(
        date=order.created_at.strftime('%B %d, %Y %H:%M')
    )}
- {email_templates['PAYMENT_METHOD'].format(payment=payment_display)}

{email_templates['ORDER_DETAILS_HEADER']}
- {email_templates['ORDER_NUMBER'].format(order_id=order.id)}
- {email_templates['ORDER_STATUS'].format(status=order.get_status_display())}

{email_templates['ITEMS_ORDERED_HEADER']}
{items_text}

{email_templates['TOTAL_HEADER'].format(total=order.total_price)}

{email_templates['SHIPPING_ADDRESS_HEADER']}
{order.shipping_address}

{email_templates['ADMIN_ACTION_REQUIRED']}
"""


def build_items_text(order: Order) -> str:
    """Build items text for email content."""
    items_text = ""
    item_format = settings.EMAIL_TEMPLATES['ITEM_FORMAT']
    for item in order.items.all():
        formatted_item = item_format.format(
            name=item.product.name,
            quantity=item.quantity,
            total=item.total
        )
        items_text += f"{formatted_item}\n"
    return items_text


def send_status_change_notification(
    order: Order, old_status: str, new_status: str
) -> None:
    """Send order status change notification.

    Args:
        order: Order instance to send notification for
        old_status: Previous order status
        new_status: New order status
    """
    from django.conf import settings

    old_status_display = get_status_display_name(old_status)
    new_status_display = get_status_display_name(new_status)
    user_name = order.user.get_full_name() or order.user.username

    customer_subject = settings.EMAIL_TEMPLATES[
        'STATUS_UPDATE_SUBJECT'
    ].format(order_id=order.id)
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


def build_status_change_email_text(
    order: Order,
    user_name: str,
    old_status_display: str,
    new_status_display: str,
    new_status: str
) -> str:
    """Build status change email text content.

    Args:
        order: Order instance to build email for
        user_name: Name of the user
        old_status_display: Display name for old status
        new_status_display: Display name for new status
        new_status: New status key

    Returns:
        Formatted status change email text content
    """
    items_text = build_items_text(order)
    status_message = get_status_change_message(new_status)
    email_templates = settings.EMAIL_TEMPLATES

    return f"""
{email_templates['STATUS_UPDATE_GREETING'].format(user_name=user_name)}

{email_templates['STATUS_UPDATE_HEADER']}

{email_templates['ORDER_DETAILS_HEADER']}
- {email_templates['ORDER_NUMBER'].format(order_id=order.id)}
- Previous Status: {old_status_display}
- New Status: {new_status_display}
- Updated Date: {order.updated_at.strftime('%B %d, %Y %H:%M')}

{email_templates['ITEMS_ORDERED_HEADER']}
{items_text}

{email_templates['TOTAL_HEADER'].format(total=order.total_price)}

{email_templates['SHIPPING_ADDRESS_HEADER']}
{order.shipping_address}

{status_message}

{email_templates['CUSTOMER_FOOTER']}

{email_templates['BEST_REGARDS']}
{email_templates['TEAM_SIGNATURE']}

{email_templates['COPYRIGHT']}
"""


def get_status_change_message(new_status: str) -> str:
    """Get message based on new status."""
    return settings.STATUS_CHANGE_MESSAGES.get(new_status, "")
