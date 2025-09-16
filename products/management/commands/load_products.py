"""
Django management command for loading product data from JSON file.
"""

import json
from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = 'Load product data from JSON file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default='products_data.json',
            help='Path to JSON file containing product data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        clear_data = options['clear']

        if clear_data:
            self.clear_existing_data()

        self.ensure_media_directories()
        self.load_products_from_json(json_file)

    def clear_existing_data(self):
        """Clear existing data."""
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS('✓ Existing data cleared')
        )

    def ensure_media_directories(self):
        """Ensure media directories exist."""
        media_dirs = [
            'media',
            'media/product_images',
            'media/profile_image'
        ]

        for dir_path in media_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            self.stdout.write(f'✓ Ensured directory exists: {dir_path}')

    def check_images_availability(self, products_data):
        """Check which images are available in media folder."""
        available_images = []
        missing_images = []

        for product_data in products_data:
            image_name = product_data['image_name']
            image_path = Path('media/product_images') / image_name

            if image_path.exists():
                available_images.append(image_name)
            else:
                missing_images.append(image_name)

        self.stdout.write(f'Available images: {len(available_images)}')
        self.stdout.write(f'Missing images: {len(missing_images)}')

        if missing_images:
            self.stdout.write('Missing images:')
            for img in missing_images:
                self.stdout.write(f'  - {img}')

        return available_images, missing_images

    def load_products_from_json(self, json_file='products_data.json'):
        """Load products from JSON file into database."""
        if not Path(json_file).exists():
            self.stdout.write(
                self.style.ERROR(f'File {json_file} not found!')
            )
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_data = data.get('categories', [])
        products_data = data.get('products', [])

        self.stdout.write(
            f'Found {len(categories_data)} categories and '
            f'{len(products_data)} products'
        )

        available_images, missing_images = self.check_images_availability(
            products_data
        )

        category_objects = {}
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'name': category_name}
            )
            category_objects[category_name] = category

        created_count = 0
        for product_data in products_data:
            try:
                category = category_objects.get(product_data['category'])
                if not category:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Category {product_data['category']} not found "
                            f"for product {product_data['name']}"
                        )
                    )
                    continue

                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    category=category,
                    price=Decimal(str(product_data['price'])),
                    stock=100,
                    is_active=True
                )

                image_name = product_data['image_name']
                image_path = Path('media/product_images') / image_name

                if image_path.exists():
                    with open(image_path, 'rb') as img_file:
                        product.image.save(
                            image_name,
                            File(img_file),
                            save=True
                        )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Loaded image for {product_data["name"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Image not found for {product_data["name"]}: '
                            f'{image_path}'
                        )
                    )

                created_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creating product {product_data["name"]}: '
                        f'{str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} products'
            )
        )
