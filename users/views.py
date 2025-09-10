from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, TemplateView, UpdateView

from orders.models import Order
from users.forms import (CustomPasswordChangeForm, EmailLoginForm,
                         ForgotPasswordForm, ResetPasswordForm,
                         UserProfileForm, UserRegisterForm)
from users.models import User


def log_to_console(template_key: str, **kwargs) -> None:
    """Helper function to log formatted messages to console."""
    if template_key in settings.CONSOLE_LOGS:
        template = settings.CONSOLE_LOGS[template_key]
        print(template.format(**kwargs))


class UserLoginView(LoginView):
    """User login view with email authentication."""
    template_name = 'users/login.html'
    form_class = EmailLoginForm

    def get_initial(self) -> dict[str, any]:
        """Get initial form data with pre-filled email if available."""
        initial = super(UserLoginView, self).get_initial()
        email = self.request.session.get('register_email')
        if email:
            initial['username'] = email
            del self.request.session['register_email']
            self.request.session.modified = True
        return initial

    def form_valid(self, form) -> HttpResponse:
        """Handle valid form submission."""
        remember_me = self.request.POST.get('remember_me') == 'on'
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(None)
        self.request.session.modified = True
        messages.success(self.request, settings.MESSAGES['login_success'])

        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(self.request, settings.MESSAGES['login_error'])
        return super().form_invalid(form)


class RegisterView(CreateView):
    """User registration view."""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form) -> HttpResponse:
        """Handle valid registration form submission."""
        user = form.save()
        self.request.session['register_email'] = user.email
        self.request.session.modified = True

        messages.add_message(
            self.request, messages.SUCCESS,
            'Registration successful! Please log in.')
        return super(RegisterView, self).form_valid(form)


class UserLogoutView(LogoutView):
    """User logout view."""
    def dispatch(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse:
        """Handle logout request with success message.

        Args:
            request: HTTP request object
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            HttpResponse redirect after logout
        """
        messages.success(request, settings.MESSAGES['logout_success'])
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AccountView(TemplateView):
    """Main account page with order history and profile tabs."""
    template_name = 'users/account.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        """Get context data for account page with orders and filters."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('search', '')
        orders = Order.objects.filter(user=user)
        if status_filter:
            orders = orders.filter(status=status_filter)
        if search_query:
            orders = orders.filter(
                Q(id__icontains=search_query) |
                Q(shipping_address__icontains=search_query)
            )

        paginator = Paginator(orders, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context.update({
            'orders': page_obj,
            'status_filter': status_filter,
            'search_query': search_query,
            'status_choices': settings.ORDER_STATUS_CHOICES,
        })

        # Add user reviews
        from products.models import Review
        context['user_reviews'] = Review.objects.filter(
            user=user
        ).select_related('product').order_by('-created_at')[:10]

        return context


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """View for updating user profile information."""
    model = get_user_model()
    form_class = UserProfileForm
    template_name = 'users/account_edit.html'
    success_url = reverse_lazy('users:account')

    def get_object(self, queryset=None) -> User:
        """Get the user object to update."""
        return self.request.user

    def form_valid(self, form) -> HttpResponse:
        """Handle valid form submission."""
        messages.success(self.request, settings.MESSAGES['profile_updated'])
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(self.request, settings.MESSAGES['profile_errors'])
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    """View for changing user password."""
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:account')

    def form_valid(self, form) -> HttpResponse:
        """Handle valid password change form submission."""
        messages.success(self.request, settings.MESSAGES['password_changed'])
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid password change form submission."""
        messages.error(self.request, settings.MESSAGES['password_errors'])
        return super().form_invalid(form)


@require_http_methods(["GET", "POST"])
def forgot_password(request: HttpRequest) -> HttpResponse:
    """View for handling password reset requests."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if user exists
            user_model = get_user_model()
            try:
                user = user_model.objects.get(email=email)

                # Store reset info in session
                request.session['password_reset_user_id'] = user.id
                request.session['password_reset_email'] = user.email
                request.session[
                    'password_reset_timestamp'] = timezone.now().timestamp()

                reset_url = (f"{request.build_absolute_uri('/')}"
                             f"users/reset-password/")

                # Email content
                subject = settings.PASSWORD_RESET_EMAIL_SUBJECT
                message = settings.PASSWORD_RESET_EMAIL_TEMPLATE.format(
                    user_name=user.first_name or user.username,
                    reset_url=reset_url
                )

                # Send email
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )

                    # Log to console
                    log_to_console('password_reset_email_sent',
                                   email=email,
                                   subject=subject,
                                   reset_url=reset_url,
                                   username=user.username,
                                   user_id=user.id,
                                   valid_until=timezone.now() +
                                   timedelta(hours=1))

                    messages.success(
                        request,
                        settings.MESSAGES['password_reset_sent']
                    )

                except Exception as e:
                    log_to_console('password_reset_email_failed',
                                   error=str(e),
                                   email=email)

                    messages.error(
                        request,
                        settings.MESSAGES['password_reset_email_failed']
                    )

            except user_model.DoesNotExist:
                # Don't reveal if email exists or not for security
                log_to_console('password_reset_user_not_found',
                               email=email)

                messages.success(
                    request,
                    settings.MESSAGES['password_reset_sent_generic']
                )

            return redirect('users:login')
    else:
        form = ForgotPasswordForm()

    return render(request, 'users/forgot_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def reset_password(request: HttpRequest) -> HttpResponse:
    """View for handling password reset with session."""
    # Check if reset session exists
    user_id = request.session.get('password_reset_user_id')
    reset_email = request.session.get('password_reset_email')
    reset_timestamp = request.session.get('password_reset_timestamp')

    if not all([user_id, reset_email, reset_timestamp]):
        log_to_console('password_reset_no_session')

        messages.error(request, settings.MESSAGES['password_reset_no_session'])
        return redirect('users:forgot_password')

    # Check if reset session is not expired (1 hour)
    current_time = timezone.now().timestamp()
    if current_time - reset_timestamp > 3600:  # 1 hour = 3600 seconds
        log_to_console('password_reset_session_expired',
                       session_time=datetime.fromtimestamp(reset_timestamp),
                       current_time=timezone.now(),
                       time_diff=(current_time - reset_timestamp) / 60)

        # Clear expired session
        request.session.pop('password_reset_user_id', None)
        request.session.pop('password_reset_email', None)
        request.session.pop('password_reset_timestamp', None)

        messages.error(request, settings.MESSAGES['password_reset_expired'])
        return redirect('users:forgot_password')

    # Get user
    user_model = get_user_model()
    try:
        user = user_model.objects.get(id=user_id, email=reset_email)

        log_to_console('password_reset_attempt',
                       username=user.username,
                       user_id=user.id,
                       email=user.email,
                       valid_until=datetime.fromtimestamp(
                           reset_timestamp + 3600))

    except user_model.DoesNotExist:
        log_to_console('password_reset_user_not_found_session',
                       user_id=user_id,
                       email=reset_email)

        messages.error(request,
                       settings.MESSAGES['password_reset_invalid_session'])
        return redirect('users:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']

            # Update user password
            user.set_password(new_password)
            user.save()

            # Clear reset session
            request.session.pop('password_reset_user_id', None)
            request.session.pop('password_reset_email', None)
            request.session.pop('password_reset_timestamp', None)

            log_to_console('password_reset_successful',
                           username=user.username,
                           user_id=user.id,
                           email=user.email)

            messages.success(request,
                             settings.MESSAGES['password_reset_success'])
            return redirect('users:login')
    else:
        form = ResetPasswordForm()

    return render(request, 'users/reset_password.html', {
        'form': form,
        'user': user
    })
