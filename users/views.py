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

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me') == 'on'
        print(f"Remember me: {remember_me}")
        print(
            f"Session expiry: {self.request.session.get_expiry_age()} seconds")
        print(f"POST data: {dict(self.request.POST)}")

        if not remember_me:
            self.request.session.set_expiry(0)

        else:
            self.request.session.set_expiry(None)

        return super(UserLoginView, self).form_valid(form)



class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        login(self.request, self.object)
        messages.success(self.request, 'Registration successful! 🎉')

        return super().form_valid(form)