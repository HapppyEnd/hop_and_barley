#!/bin/bash

set -e

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

echo "Making migrations..."
python manage.py makemigrations

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin user..."
python manage.py create_admin

echo "Loading product data..."
python manage.py load_products --clear

echo "Starting server..."
exec "$@"
