from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='profile_image', null=True, blank=True,
                               default='profile_image/default.jpg')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']


    def __str__(self):
        return self.email

