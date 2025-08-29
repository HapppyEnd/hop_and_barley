from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import EmailLoginForm, UserRegisterForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = EmailLoginForm

    def get_initial(self):
        initial = super(UserLoginView, self).get_initial()
        email = self.request.session.get('register_email')
        if email:
            initial['username'] = email
            # Clear session after use
            del self.request.session['register_email']
            self.request.session.modified = True
        return initial

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me') == 'on'
        if not remember_me:
            # If "remember me" is not checked,
            # session will expire when browser closes
            self.request.session.set_expiry(0)
        else:
            # If checked, use settings from settings.py
            self.request.session.set_expiry(None)
        
        # Ensure session is saved
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
    
        # Save email in session for auto-filling login form
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
