import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from phonenumber_field.phonenumber import PhoneNumber

from tests.factories import UserFactory
from users.forms import (CustomPasswordChangeForm, EmailLoginForm,
                         ForgotPasswordForm, ResetPasswordForm,
                         UserProfileForm, UserRegisterForm)


@pytest.mark.django_db
class TestEmailLoginForm:
    """Test cases for EmailLoginForm."""

    @pytest.mark.form
    def test_form_valid_data(self):
        """Test form with valid data."""
        UserFactory(email='test@example.com', password='testpass123')
        form_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        form = EmailLoginForm(data=form_data)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_invalid_email(self):
        """Test form with invalid email."""
        form_data = {
            'username': 'invalid-email',
            'password': 'testpass123'
        }
        form = EmailLoginForm(data=form_data)
        assert not form.is_valid()
        assert 'username' in form.errors

    @pytest.mark.form
    def test_form_empty_data(self):
        """Test form with empty data."""
        form = EmailLoginForm(data={})
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'password' in form.errors

    @pytest.mark.form
    def test_form_widget_attributes(self):
        """Test form widget attributes."""
        form = EmailLoginForm()
        assert 'class' in form.fields['username'].widget.attrs
        assert 'placeholder' in form.fields['username'].widget.attrs
        assert 'class' in form.fields['password'].widget.attrs
        assert 'placeholder' in form.fields['password'].widget.attrs


@pytest.mark.django_db
class TestUserRegisterForm:
    """Test cases for UserRegisterForm."""

    @pytest.mark.form
    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+12345678901',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegisterForm(data=form_data)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_email_uniqueness_validation(self):
        """Test email uniqueness validation."""
        UserFactory(email='existing@example.com')
        form_data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegisterForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    @pytest.mark.form
    def test_form_password_mismatch(self):
        """Test password mismatch validation."""
        form_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        form = UserRegisterForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    @pytest.mark.form
    def test_form_phone_validation(self):
        """Test phone number validation."""
        form_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'phone': '+12345678901',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegisterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == PhoneNumber.from_string('+12345678901')

    @pytest.mark.form
    def test_form_optional_phone(self):
        """Test form with optional phone field."""
        form_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'phone': '',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegisterForm(data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
class TestUserProfileForm:
    """Test cases for UserProfileForm."""

    @pytest.mark.form
    def test_form_valid_data(self):
        """Test form with valid data."""
        user = UserFactory()
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': user.email,
            'phone': '+12345678901',
            'city': 'New City',
            'address': 'New Address'
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_email_readonly(self):
        """Test email field is readonly."""
        user = UserFactory(email='original@example.com')
        form = UserProfileForm(instance=user)
        assert form.fields['email'].widget.attrs.get('readonly')

    @pytest.mark.form
    def test_form_email_cannot_be_changed(self):
        """Test email cannot be changed through form."""
        user = UserFactory(email='original@example.com')
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'different@example.com',
            'phone': '+12345678901'
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()
        assert form.cleaned_data['email'] == 'original@example.com'

    @pytest.mark.form
    def test_form_phone_validation(self):
        """Test phone number validation."""
        user = UserFactory()
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': user.email,
            'phone': '+12345678901'
        }
        form = UserProfileForm(data=form_data, instance=user)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == PhoneNumber.from_string('+12345678901')

    @pytest.mark.form
    def test_form_image_upload(self):
        """Test image upload field."""
        user = UserFactory()

        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'

        image_file = SimpleUploadedFile(
            'test_image.jpg',
            jpeg_header,
            content_type='image/jpeg'
        )
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': user.email,
            'phone': '',
            'city': 'Test City',
            'address': 'Test Address'
        }
        files = {'image': image_file}
        form = UserProfileForm(data=form_data, files=files, instance=user)
        assert form.is_valid()


@pytest.mark.django_db
class TestCustomPasswordChangeForm:
    """Test cases for CustomPasswordChangeForm."""

    @pytest.mark.form
    def test_form_valid_data(self):
        """Test form with valid data."""
        user = UserFactory()
        form_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = CustomPasswordChangeForm(user=user, data=form_data)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_wrong_old_password(self):
        """Test form with wrong old password."""
        user = UserFactory()
        form_data = {
            'old_password': 'wrongpass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = CustomPasswordChangeForm(user=user, data=form_data)
        assert not form.is_valid()
        assert 'old_password' in form.errors

    @pytest.mark.form
    def test_form_password_mismatch(self):
        """Test form with password mismatch."""
        user = UserFactory()
        form_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass'
        }
        form = CustomPasswordChangeForm(user=user, data=form_data)
        assert not form.is_valid()
        assert 'new_password2' in form.errors

    @pytest.mark.form
    def test_form_widget_attributes(self):
        """Test form widget attributes."""
        user = UserFactory()
        form = CustomPasswordChangeForm(user=user)
        assert 'class' in form.fields['old_password'].widget.attrs
        assert 'placeholder' in form.fields['old_password'].widget.attrs
        assert form.fields['new_password1'].help_text is None
        assert form.fields['new_password2'].help_text is None


@pytest.mark.django_db
class TestForgotPasswordForm:
    """Test cases for ForgotPasswordForm."""

    @pytest.mark.form
    def test_form_valid_email(self):
        """Test form with valid email."""
        form_data = {'email': 'test@example.com'}
        form = ForgotPasswordForm(data=form_data)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_invalid_email(self):
        """Test form with invalid email."""
        form_data = {'email': 'invalid-email'}
        form = ForgotPasswordForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    @pytest.mark.form
    def test_form_empty_email(self):
        """Test form with empty email."""
        form = ForgotPasswordForm(data={})
        assert not form.is_valid()
        assert 'email' in form.errors


@pytest.mark.django_db
class TestResetPasswordForm:
    """Test cases for ResetPasswordForm."""

    @pytest.mark.form
    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = ResetPasswordForm(data=form_data)
        assert form.is_valid()

    @pytest.mark.form
    def test_form_password_mismatch(self):
        """Test form with password mismatch."""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'differentpass'
        }
        form = ResetPasswordForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors

    @pytest.mark.form
    def test_form_short_password(self):
        """Test form with short password."""
        form_data = {
            'new_password1': 'short',
            'new_password2': 'short'
        }
        form = ResetPasswordForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors

    @pytest.mark.form
    def test_form_empty_data(self):
        """Test form with empty data."""
        form = ResetPasswordForm(data={})
        assert not form.is_valid()
        assert 'new_password1' in form.errors
        assert 'new_password2' in form.errors
