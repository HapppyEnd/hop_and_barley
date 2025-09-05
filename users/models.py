from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Custom user model."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_image', null=True, blank=True,
                              default='profile_image/default.jpg')
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
