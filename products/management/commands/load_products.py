import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = 'Load products from JSON file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default='products_data.json',
            help='JSON file containing products data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products and categories before loading'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        clear_existing = options['clear']

        if not Path(json_file).exists():
            self.stdout.write(
                self.style.ERROR(f'JSON file {json_file} not found!')
            )
            return

        if clear_existing:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write('Existing data cleared')

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_data = data.get('categories', [])
        products_data = data.get('products', [])

        self.stdout.write(f'Found {len(categories_data)} categories and {len(products_data)} products')

        # Create categories
        category_objects = {}
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'name': category_name}
            )
            category_objects[category_name] = category
            if created:
                self.stdout.write(f'Created category: {category_name}')
            else:
                self.stdout.write(f'Using existing category: {category_name}')

        # Create products
        created_count = 0
        for product_data in products_data:
            try:
                category = category_objects.get(product_data['category'])
                if not category:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Category {product_data["category"]} not found for product {product_data["name"]}'
                        )
                    )
                    continue

                product = Product.objects.create(
                    name=product_data['name'],
                    description=product_data['description'],
                    category=category,
                    price=Decimal(str(product_data['price'])),
                    image=f"product_images/{product_data['image_name']}",
                    stock=100,
                    is_active=True
                )
                created_count += 1
                self.stdout.write(f'Created product: {product.name} (${product.price})')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating product {product_data["name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} products')
        )
