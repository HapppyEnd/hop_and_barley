from django.urls import path

from users.views import (AccountView, PasswordChangeView, ProfileUpdateView,
                         RegisterView, UserLoginView, UserLogoutView,
                         forgot_password)

app_name = 'users'
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('account/', AccountView.as_view(), name='account'),
    path('account/edit/', ProfileUpdateView.as_view(), name='account_edit'),
    path('password/change/', PasswordChangeView.as_view(),
         name='password_change'),

    path('forgot-password/', forgot_password, name='forgot_password'),
]
