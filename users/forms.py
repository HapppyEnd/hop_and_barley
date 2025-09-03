from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       UserCreationForm)
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
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(
            attrs={'class': 'input',
                   'placeholder': 'repeat your password'}))

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return phone


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    phone = PhoneNumberField(
        label='Phone Number',
        required=False,
        widget=forms.TextInput(

            attrs={'class': 'Input', 'placeholder': 'Phone Number'}
        )
    )

    class Meta:
        model = get_user_model()
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'city', 'address'
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'Input', 'placeholder': 'First Name'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'Input', 'placeholder': 'Last Name'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'Input', 'placeholder': 'Email Address'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'Input', 'placeholder': 'City'}
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'Textarea', 'placeholder': 'Address', 'rows': 3
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self):
        """Ensure email cannot be changed."""
        return self.instance.email

    def clean_phone(self):
        """Validate phone number."""
        phone = self.cleaned_data.get('phone')
        if phone:
            return phone
        return phone


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Current Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'Input',
            'placeholder': 'Confirm New Password'
        })

        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None


class ForgotPasswordForm(forms.Form):
    """Form for password reset request."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(
            attrs={'class': 'Input', 'placeholder': 'Enter your email address'}
        )
    )
