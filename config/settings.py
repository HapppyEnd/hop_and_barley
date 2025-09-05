import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'phonenumber_field',
    'users.apps.UsersConfig',
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
    'api.apps.ApiConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ]
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/products'
LOGOUT_REDIRECT_URL = '/products'


# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = False  # Set to True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

# Cart settings
CART_SESSION_ID = 'cart'

# Business logic constants
# Order statuses
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PLACED = 'placed'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELED = 'canceled'

ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_PLACED, 'Placed'),
    (ORDER_STATUS_PAID, 'Paid'),
    (ORDER_STATUS_SHIPPED, 'Shipped'),
    (ORDER_STATUS_DELIVERED, 'Delivered'),
    (ORDER_STATUS_CANCELED, 'Canceled'),
)

# Statuses that allow order cancellation
CANCELLABLE_STATUSES = [
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PLACED,
    ORDER_STATUS_PAID,
]

# Payment methods
PAYMENT_METHOD_CARD = 'card'
PAYMENT_METHOD_CASH_ON_DELIVERY = 'cash_on_delivery'

PAYMENT_METHOD_CHOICES = (
    (PAYMENT_METHOD_CARD, 'Credit/Debit Card'),
    (PAYMENT_METHOD_CASH_ON_DELIVERY, 'Cash on Delivery'),
)

# Payment method display names
PAYMENT_DISPLAY_NAMES = {
    PAYMENT_METHOD_CARD: 'Credit/Debit Card',
    PAYMENT_METHOD_CASH_ON_DELIVERY: 'Cash on Delivery',
}

# Order messages
ORDER_MESSAGES = {
    'CART_EMPTY': 'Your cart is empty',
    'INVALID_QUANTITY': 'Invalid quantity',
    'PAYMENT_FAILED': (
        'Payment failed. Please try again with a different payment method.'
    ),
    'ORDER_ERROR': 'Error placing order: {error}',
    'SHIPPING_ADDRESS_REQUIRED': 'Please provide shipping address',
    'ORDER_CANNOT_BE_CANCELED': 'This order cannot be canceled.',
    'ORDER_CANCELED_SUCCESS': 'Order has been canceled successfully.',
    'ORDER_STATUS_UPDATED': 'Order status updated to {status}',
    'INVALID_STATUS': 'Invalid status selected.',
    'ORDER_CONFIRMATION_COD': (
        'Order successfully placed! You will pay Cash on Delivery '
        'when you receive your order.'
    ),
    'ORDER_CONFIRMATION_PAID': (
        'Order successfully placed and paid! '
        'Check your email for confirmation.'
    ),
}

# Status change messages
STATUS_CHANGE_MESSAGES = {
    ORDER_STATUS_PLACED: (
        "Your order has been confirmed and is being prepared. "
        "You will pay when you receive your order.\n\n"
    ),
    ORDER_STATUS_PAID: (
        "Your order has been paid and is being processed. "
        "We'll prepare it for shipping soon.\n\n"
    ),
    ORDER_STATUS_SHIPPED: (
        "Your order has been shipped and is on its way to you. "
        "You should receive it soon.\n\n"
    ),
    ORDER_STATUS_DELIVERED: (
        "Your order has been delivered. Thank you for your purchase!\n\n"
    ),
    ORDER_STATUS_CANCELED: (
        "Your order has been canceled. If you have any questions, "
        "please contact us.\n\n"
    ),
}

# Email settings
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'  # For development
)
# For production, uncomment and configure:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # or another SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'noreply@hopandbarley.com'
# ADMIN_EMAIL = 'admin@hopandbarley.com'