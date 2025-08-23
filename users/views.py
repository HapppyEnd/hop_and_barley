# users/views.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import EmailLoginForm, UserRegisterForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = EmailLoginForm

    def get_initial(self):
        initial = super(UserLoginView, self).get_initial()
        email = self.request.session.get('email')
        if email:
            initial['username'] = email
        return initial

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me') == 'on'
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(None)
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()

        self.request.session['register_email'] = user.email
        messages.add_message(
            self.request, messages.SUCCESS,
            'Registration successful! Please log in.')
        return super(RegisterView, self).form_valid(form)


