from django.conf.urls import static
from django.contrib.auth.views import LoginView
from django.urls import path
from config import settings

app_name = 'users'
urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
]

