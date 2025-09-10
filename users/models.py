from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Custom user model with email authentication and additional fields.

    Extends Django's AbstractUser to use email as the primary identifier
    and adds profile information like phone, image, city, and address.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    email = models.EmailField(
        unique=True,
        help_text="User's email address (used for login)"
    )
    phone = PhoneNumberField(
        null=True,
        blank=True,
        help_text="User's phone number"
    )
    image = models.ImageField(
        upload_to='profile_image',
        null=True,
        blank=True,
        default='profile_image/default.jpg',
        help_text="User's profile image"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's city"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="User's full address"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """Return the user's full name or username if not available."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
