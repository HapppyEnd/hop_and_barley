from django.contrib import messages
from django.contrib.auth.views import LoginView
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
            # Очищаем сессию после использования
            del self.request.session['register_email']
            self.request.session.modified = True
        return initial

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me') == 'on'
        if not remember_me:
            # Если "запомнить меня" не отмечен, 
            # сессия истечет при закрытии браузера
            self.request.session.set_expiry(0)
        else:
            # Если отмечен, используем настройки из settings.py
            self.request.session.set_expiry(None)
        
        # Убеждаемся, что сессия сохранена
        self.request.session.modified = True
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
    
        # Сохраняем email в сессии для автозаполнения формы входа
        self.request.session['register_email'] = user.email
        self.request.session.modified = True

        messages.add_message(
            self.request, messages.SUCCESS,
            'Registration successful! Please log in.')
        return super(RegisterView, self).form_valid(form)
