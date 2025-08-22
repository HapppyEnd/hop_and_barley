from django.contrib.auth.forms import AuthenticationForm
from django import forms


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'input', 'placeholder': 'enter your email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'enter your password'}))
