#!/usr/bin/env python3
"""
Script for loading product data from JSON file into database.
Used for loading data into PostgreSQL container.
"""

import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import django
from django.core.files import File

from products.models import Category, Product

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def check_images_availability(products_data):
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

    print(f"Available images: {len(available_images)}")
    print(f"Missing images: {len(missing_images)}")

    if missing_images:
        print("Missing images:")
        for img in missing_images:
            print(f"  - {img}")

    return available_images, missing_images


def load_products_from_json(json_file='products_data.json'):
    """Load products from JSON file into database.

    Args:
        json_file (str): Path to JSON file containing product data
    """

    if not Path(json_file).exists():
        print(f"File {json_file} not found!")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    categories_data = data.get('categories', [])
    products_data = data.get('products', [])

    print(f"Found {len(categories_data)} categories and "
          f"{len(products_data)} products")

    available_images, missing_images = check_images_availability(products_data)

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
                print(f"Category {product_data['category']} not found "
                      f"for product {product_data['name']}")
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
                print(f"✓ Loaded image for {product_data['name']}")
            else:
                print(f"⚠ Image not found for {product_data['name']}: "
                      f"{image_path}")

            created_count += 1

        except Exception as e:
            print(f"Error creating product {product_data['name']}: {str(e)}")

    print(f"Successfully created {created_count} products")


def clear_existing_data():
    """Clear existing data (optional)."""
    import sys
    if sys.stdin.isatty():
        response = input("Clear existing data? (y/N): ")
        if response.lower() == 'y':
            Product.objects.all().delete()
            Category.objects.all().delete()
            print("Existing data cleared")
    else:
        Product.objects.all().delete()
        Category.objects.all().delete()
        print("Existing data cleared (non-interactive mode)")


def ensure_media_directories():
    """Ensure media directories exist."""
    media_dirs = [
        'media',
        'media/product_images',
        'media/profile_image'
    ]

    for dir_path in media_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory exists: {dir_path}")


def main():
    """Main function to load product data."""
    print("Loading product data into database...")

    ensure_media_directories()

    clear_existing_data()

    load_products_from_json()

    print("Loading completed!")


if __name__ == '__main__':
    main()
