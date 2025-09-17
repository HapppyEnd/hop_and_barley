"""
Django management command for creating admin superuser.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin superuser'

    def handle(self, *args, **options):
        self.create_superuser()

        self.stdout.write(
            self.style.SUCCESS('✓ Admin user created successfully!')
        )

    def create_superuser(self):
        """Create superuser if it doesn't exist."""
        username = 'admin'
        email = 'admin@hopandbarley.com'
        password = 'admin123'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'✓ Admin user with email "{email}" already exists')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Admin user created: {email} / {password}'
            )
        )
