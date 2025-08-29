from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Fix incorrect product prices'

    def handle(self, *args, **options):
        # Исправляем цену Mosaic Hops
        try:
            mosaic = Product.objects.get(name='Mosaic Hops')
            self.stdout.write(
                f'Found {mosaic.name}, current price: {mosaic.price}'
            )
            
            # Устанавливаем правильную цену
            mosaic.price = 3.99
            mosaic.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Fixed price for {mosaic.name}: {mosaic.price}'
                )
            )
            
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Product "Mosaic Hops" not found')
            )
        
        # Проверяем другие товары с подозрительными ценами
        self.stdout.write('\nChecking for other price issues:')
        for product in Product.objects.all():
            if product.price > 100:
                self.stdout.write(
                    self.style.WARNING(
                        f'WARNING: {product.name} has high price: {product.price}'
                    )
                )
