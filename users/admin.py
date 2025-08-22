from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'image')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
