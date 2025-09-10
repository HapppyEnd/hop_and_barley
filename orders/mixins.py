from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest

from orders.models import Order


class OrderPermissionMixin:
    """Mixin for order permission checks."""

    @staticmethod
    def can_modify_order(user: AbstractUser, order: Order) -> bool:
        """Check if user can modify order."""
        return user.is_staff or order.user == user

    @staticmethod
    def check_order_permission(
        request: HttpRequest,
        user: AbstractUser,
        order: Order,
        error_message: str = 'You do not have permission to access this order.'
    ) -> bool:
        """Check order permission and show error if not allowed."""
        if not OrderPermissionMixin.can_modify_order(user, order):
            messages.error(request, error_message)
            return False
        return True
