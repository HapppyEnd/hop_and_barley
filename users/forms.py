from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       UserCreationForm)
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    """Login form using email instead of username."""
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(
            attrs={'class': 'input', 'placeholder': 'Enter your email'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'Enter your password'}
        )
    )


class UserRegisterForm(UserCreationForm):
    """User registration form with additional fields."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(
            attrs={'class': 'input', 'placeholder': 'Enter your email'}
        )
    )
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'enter your username'}
        )
    )
    phone = PhoneNumberField(
        label='Phone number',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'enter your phone number'}
        )
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'enter your password'}
        )
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(
            attrs={'class': 'input', 'placeholder': 'repeat your password'}
        )
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone',)

    def clean_email(self) -> str:
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email

    def clean_phone(self) -> Any:
        """Validate phone number."""
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
        fields = ('first_name', 'last_name', 'email', 'phone', 'city',
                  'address', 'image')
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
            'image': forms.FileInput(
                attrs={'class': 'Input', 'accept': 'image/*'}
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        """Initialize form with readonly email field."""
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self) -> str:
        """Ensure email cannot be changed."""
        return self.instance.email

    def clean_phone(self) -> Any:
        """Validate phone number."""
        phone = self.cleaned_data.get('phone')
        return phone


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with better styling."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize form with custom styling."""
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


class ResetPasswordForm(forms.Form):
    """Form for password reset with new password."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(
            attrs={'class': 'Input', 'placeholder': 'Enter new password'}
        )
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(
            attrs={'class': 'Input', 'placeholder': 'Confirm new password'}
        )
    )

    def clean(self) -> dict[str, Any]:
        """Validate password fields."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Passwords don't match.")
            if len(new_password1) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long.")

        return cleaned_data
