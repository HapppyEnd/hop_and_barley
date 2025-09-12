#!/usr/bin/env python3
"""
Скрипт для загрузки данных о продуктах из JSON файла в базу данных.
Используется для загрузки данных в PostgreSQL контейнер.
"""

import os
import sys
from pathlib import Path

import django

# Добавить путь к проекту Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import json
from decimal import Decimal

from products.models import Category, Product


def load_products_from_json(json_file='products_data.json'):
    """Загрузить продукты из JSON файла в базу данных"""
    
    if not Path(json_file).exists():
        print(f"Файл {json_file} не найден!")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    categories_data = data.get('categories', [])
    products_data = data.get('products', [])

    print(f"Найдено {len(categories_data)} категорий и {len(products_data)} продуктов")

    # Создать категории
    category_objects = {}
    for category_name in categories_data:
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'name': category_name}
        )
        category_objects[category_name] = category
        if created:
            print(f"Создана категория: {category_name}")
        else:
            print(f"Используется существующая категория: {category_name}")

    # Создать продукты
    created_count = 0
    for product_data in products_data:
        try:
            # Получить категорию
            category = category_objects.get(product_data['category'])
            if not category:
                print(f"Категория {product_data['category']} не найдена для продукта {product_data['name']}")
                continue

            # Создать продукт
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                category=category,
                price=Decimal(str(product_data['price'])),
                image=f"product_images/{product_data['image_name']}",
                stock=100,  # По умолчанию
                is_active=True
            )
            created_count += 1
            print(f"Создан продукт: {product.name} (${product.price})")
            
        except Exception as e:
            print(f"Ошибка при создании продукта {product_data['name']}: {str(e)}")

    print(f"\nУспешно создано {created_count} продуктов")


def clear_existing_data():
    """Очистить существующие данные (опционально)"""
    response = input("Очистить существующие данные? (y/N): ")
    if response.lower() == 'y':
        Product.objects.all().delete()
        Category.objects.all().delete()
        print("Существующие данные очищены")


def main():
    """Основная функция"""
    print("Загрузка данных о продуктах в базу данных...")
    
    # Опционально очистить существующие данные
    clear_existing_data()
    
    # Загрузить данные
    load_products_from_json()
    
    print("Загрузка завершена!")


if __name__ == '__main__':
    main()
