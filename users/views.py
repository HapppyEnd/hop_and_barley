from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, TemplateView, UpdateView

from orders.models import Order
from users.forms import (CustomPasswordChangeForm, EmailLoginForm,
                         ForgotPasswordForm, UserProfileForm, UserRegisterForm)


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = EmailLoginForm

    def get_initial(self):
        initial = super(UserLoginView, self).get_initial()
        email = self.request.session.get('register_email')
        if email:
            initial['username'] = email
            del self.request.session['register_email']
            self.request.session.modified = True
        return initial

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me') == 'on'
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(None)
        self.request.session.modified = True
        messages.success(self.request, 'Successfully logged in!')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
                       'Invalid email or password. Please try again.')
        return super().form_invalid(form)


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        self.request.session['register_email'] = user.email
        self.request.session.modified = True

        messages.add_message(
            self.request, messages.SUCCESS,
            'Registration successful! Please log in.')
        return super(RegisterView, self).form_valid(form)


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Successfully logged out!')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AccountView(TemplateView):
    """Main account page with order history and profile tabs."""
    template_name = 'users/account.html'

    def get_context_data(self, **kwargs):
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
            'status_choices': Order.STATUS_CHOICES,
        })

        return context


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """View for updating user profile information."""
    model = get_user_model()
    form_class = UserProfileForm
    template_name = 'users/account_edit.html'
    success_url = reverse_lazy('users:account')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(PasswordChangeView):
    """View for changing user password."""
    form_class = CustomPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:account')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """View for handling password reset requests."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                'Password reset instructions have been sent to your email.'
            )
            return redirect('users:login')
    else:
        form = ForgotPasswordForm()

    return render(request, 'users/forgot_password.html', {'form': form})
