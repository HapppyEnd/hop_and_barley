from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email Address',
                                widget=forms.EmailInput(
                                    attrs={'class': 'input',
                                           'placeholder': 'Enter your email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'Enter your password'}))


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(
            attrs={'class': 'input', 'placeholder': 'Enter your email'}),)
    username = forms.CharField(label='Username', widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'enter your username'}))
    phone = PhoneNumberField(
        label='Phone number', required=False,
        widget=forms.TextInput(
            attrs={'class': 'input',
                   'placeholder': 'enter your phone number'}))
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'enter your password'}))
    password2 = forms.CharField(label='Confirm password',
                                widget=forms.PasswordInput(
                                    attrs={'class': 'input',
                                           'placeholder': 'repeat your password'}))

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name', 'phone',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return phone
