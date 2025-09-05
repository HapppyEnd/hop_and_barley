from django.contrib import messages


class OrderPermissionMixin:
    """Mixin for order permission checks."""

    @staticmethod
    def can_modify_order(user, order):
        """Check if user can modify order."""
        return user.is_staff or order.user == user

    @staticmethod
    def check_order_permission(request, user, order,
                               error_message='You do not have permission to '
                                             'access this order.'):
        """Check order permission and show error if not allowed."""
        if not OrderPermissionMixin.can_modify_order(user, order):
            messages.error(request, error_message)
            return False
        return True
