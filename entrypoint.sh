#!/bin/bash

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

echo "Running migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Load initial data
echo "Checking if products exist..."
python manage.py shell -c "
from products.models import Product
if Product.objects.count() == 0:
    print('No products found, loading initial data...')
    import subprocess
    subprocess.run(['python', 'manage.py', 'load_products', '--json-file', 'products_data.json'], check=False)
else:
    print('Products already exist, skipping data load')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating media directories..."
mkdir -p /app/media/product_images
mkdir -p /app/media/profile_image

echo "Starting server..."
exec "$@"
