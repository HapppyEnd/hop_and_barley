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

from products.models import Category, Product

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


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

    print(
        f"Found {len(categories_data)} categories and {len(products_data)} products")

    # Create categories
    category_objects = {}
    for category_name in categories_data:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'name': category_name}
        )
        category_objects[category_name] = category

    # Create products
    created_count = 0
    for product_data in products_data:
        try:
            category = category_objects.get(product_data['category'])
            if not category:
                print(
                    f"Category {product_data['category']} not found for product {product_data['name']}")
                continue

            Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                category=category,
                price=Decimal(str(product_data['price'])),
                image=f"product_images/{product_data['image_name']}",
                stock=100,
                is_active=True
            )
            created_count += 1

        except Exception as e:
            print(f"Error creating product {product_data['name']}: {str(e)}")

    print(f"Successfully created {created_count} products")


def clear_existing_data():
    """Clear existing data (optional)."""
    response = input("Clear existing data? (y/N): ")
    if response.lower() == 'y':
        Product.objects.all().delete()
        Category.objects.all().delete()
        print("Existing data cleared")


def main():
    """Main function to load product data."""
    print("Loading product data into database...")

    # Optionally clear existing data
    clear_existing_data()

    # Load data
    load_products_from_json()

    print("Loading completed!")


if __name__ == '__main__':
    main()
