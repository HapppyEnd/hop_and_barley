from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest

from orders.models import Order


class OrderPermissionMixin:
    """Mixin for order permission checks.

    Provides methods to check if a user has permission to modify
    or access specific orders based on ownership or staff status.
    """

    @staticmethod
    def can_modify_order(user: AbstractUser, order: Order) -> bool:
        """Check if user can modify order.

        Args:
            user: User instance to check permissions for
            order: Order instance to check access to

        Returns:
            True if user can modify the order, False otherwise
        """
        return user.is_staff or order.user == user

    @staticmethod
    def check_order_permission(
        request: HttpRequest,
        user: AbstractUser,
        order: Order,
        error_message: str = 'You do not have permission to access this order.'
    ) -> bool:
        """Check order permission and show error if not allowed.

        Args:
            request: Django HTTP request object
            user: User instance to check permissions for
            order: Order instance to check access to
            error_message: Custom error message to display

        Returns:
            True if user has permission, False otherwise
        """
        if not OrderPermissionMixin.can_modify_order(user, order):
            messages.error(request, error_message)
            return False
        return True
