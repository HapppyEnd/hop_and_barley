import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
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

# Database configuration
# Check if we're in Docker by looking for Docker environment variable
is_docker = os.getenv('DOCKER_CONTAINER') == 'true'
database_url = os.getenv('DATABASE_URL')

if is_docker and database_url:
    # Docker - use DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development - use SQLite
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
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.PageNumberPagination'
    ),
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Hop & Barley API',
    'DESCRIPTION': 'API for brewing equipment online store',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'tryItOutEnabled': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
    },
    'OPERATION_ID_GENERATOR': (
        'drf_spectacular.utils.camelize_operation_id_generator'
    ),
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': (
        'rest_framework_simplejwt.authentication.'
        'default_user_authentication_rule'
    ),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/products'
LOGOUT_REDIRECT_URL = '/products'


# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_SECURE = False  # Set to True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

# CSRF settings for Docker
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access for AJAX
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

# Cart settings
CART_SESSION_ID = 'cart'

# Pagination settings
PRODUCTS_PER_PAGE = 9
ORDERS_PER_PAGE = 10

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
    'CARD_EXPIRED': 'Your card has expired. Please use a valid card.',
    'CARD_INVALID_FORMAT': 'Please enter expiry date in MM/YY format.',
    'CARD_INVALID_MONTH': 'Please enter a valid month (01-12).',
    'CARD_INVALID_YEAR': 'Please enter a valid year.',
    'CARD_NUMBER_INVALID': 'Please enter a valid card number.',
    'CARD_HOLDER_INVALID': 'Please enter cardholder name.',
    'CARD_CVV_INVALID': 'Please enter a valid CVV.',
    'CARD_DETAILS_REQUIRED': 'Please fill in all card details.',
    'CARD_NUMBER_LENGTH': 'Please enter a valid card number.',
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

# Email templates
EMAIL_TEMPLATES = {
    'CUSTOMER_GREETING': 'Dear {user_name},',
    'CUSTOMER_THANK_YOU': (
        'Thank you for your order! We\'ve received your order and are '
        'processing it.'
    ),
    'ORDER_DETAILS_HEADER': 'Order Details:',
    'ORDER_NUMBER': 'Order Number: #{order_id}',
    'ORDER_DATE': 'Order Date: {date}',
    'ORDER_STATUS': 'Status: {status}',
    'PAYMENT_METHOD': 'Payment Method: {payment}',
    'ITEMS_ORDERED_HEADER': 'Items Ordered:',
    'TOTAL_HEADER': 'Total: {total}',
    'SHIPPING_ADDRESS_HEADER': 'Shipping Address:',
    'CUSTOMER_FOOTER': (
        'We\'ll send you another email when your order ships.\n'
        'If you have any questions, please don\'t hesitate to contact us.'
    ),
    'BEST_REGARDS': 'Best regards,',
    'TEAM_SIGNATURE': 'The Hop & Barley Team',
    'COPYRIGHT': '© 2025 Hop & Barley. All rights reserved.',

    'ADMIN_ALERT_HEADER': 'New Order Alert!',
    'ADMIN_ALERT_MESSAGE': (
        'A new order has been placed and requires your attention.'
    ),
    'CUSTOMER_INFO_HEADER': 'Customer Information:',
    'CUSTOMER_NAME': 'Name: {name}',
    'CUSTOMER_EMAIL': 'Email: {email}',
    'ORDER_DATE_TIME': 'Order Date: {date}',
    'ADMIN_ACTION_REQUIRED': (
        'Action Required: Please process this order and update the status '
        'accordingly.'
    ),

    'ITEM_FORMAT': '- {name} × {quantity} - {total}',

    'STATUS_UPDATE_SUBJECT': 'Order Status Update #{order_id} - Hop & Barley',
    'STATUS_UPDATE_GREETING': 'Dear {user_name},',
    'STATUS_UPDATE_HEADER': 'Your order status has been updated!',
    'STATUS_UPDATE_DETAILS': (
        'Order #{order_id} status changed from {old_status} to {new_status}.'
    ),
    'STATUS_UPDATE_MESSAGE': 'We\'ll keep you updated on your order progress.',
    'STATUS_UPDATE_FOOTER': 'Thank you for choosing Hop & Barley!',
}

# Status change messages
STATUS_CHANGE_MESSAGES = {
    ORDER_STATUS_PLACED: (
        'Your order has been confirmed and is being prepared. '
        'You will pay when you receive your order.\n\n'
    ),
    ORDER_STATUS_PAID: (
        'Your order has been paid and is being processed. '
        'We\'ll prepare it for shipping soon.\n\n'
    ),
    ORDER_STATUS_SHIPPED: (
        'Your order has been shipped and is on its way to you. '
        'You should receive it soon.\n\n'
    ),
    ORDER_STATUS_DELIVERED: (
        'Your order has been delivered. Thank you for your purchase!\n\n'
    ),
    ORDER_STATUS_CANCELED: (
        'Your order has been canceled. If you have any questions, '
        'please contact us.\n\n'
    ),
}

# Review messages
REVIEW_DELIVERY_REQUIRED = (
    'You can only review products after they have been delivered.'
)
REVIEW_ALREADY_EXISTS = 'You have already reviewed this product.'
REVIEW_SUCCESS_MESSAGE = 'Thank you for your review!'
REVIEW_AFTER_DELIVERY = 'You can review after delivery'
REVIEW_ALREADY_REVIEWED = 'You have reviewed this product'
LOGIN_TO_REVIEW = 'Login to Review'
WRITE_REVIEW = 'Write Review'
SUBMIT_REVIEW = 'Submit Review'
CANCEL = 'Cancel'

# Review form labels
RATING_LABEL = 'Rating'
TITLE_LABEL = 'Title (optional)'
COMMENT_LABEL = 'Your Review'

# Review form placeholders
TITLE_PLACEHOLDER = 'Review title (optional)'
COMMENT_PLACEHOLDER = 'Write your review here...'

# Product category specifications
CATEGORY_SPECIFICATIONS = {
    'Malt': {
        'type': 'Specialty Malt',
        'usage': 'Typically 3-15% of the grist',
        'recommended_styles': 'Pale Ale, Amber Ale, IPA, Brown Ale, Porter'
    },
    'Hops': {
        'type': 'Aroma/Flavor Hop',
        'usage': 'Late boil additions and dry hopping',
        'recommended_styles': 'Pale Ale, IPA, American Wheat, Saison'
    },
    'Yeast': {
        'type': 'Ale Yeast',
        'usage': 'Primary fermentation',
        'recommended_styles': 'American Ales, IPAs, Wheat Beers'
    },
    'Beer Kits': {
        'type': 'Complete Brewing Kit',
        'usage': 'All ingredients for one batch',
        'recommended_styles': 'Beginner to Intermediate difficulty'
    },
    'Equipment': {
        'type': 'Brewing Equipment',
        'usage': 'Essential brewing tools and hardware',
        'recommended_styles': 'All beer styles'
    },
    'Additives': {
        'type': 'Brewing Additive',
        'usage': 'Enhance flavor, clarity, or stability',
        'recommended_styles': 'Various styles depending on additive'
    }
}

# Default specifications for unknown categories
DEFAULT_CATEGORY_SPECIFICATIONS = {
    'type': 'Brewing Ingredient',
    'usage': 'Check product description for details',
    'recommended_styles': 'Contact us for specific brewing recommendations'
}

# Email settings
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

# For production, uncomment and configure:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # or another SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

# Email configuration
DEFAULT_FROM_EMAIL = 'noreply@hopandbarley.com'
ADMIN_EMAIL = 'admin@hopandbarley.com'

# Email templates
PASSWORD_RESET_EMAIL_SUBJECT = 'Password Reset - Hop & Barley'
PASSWORD_RESET_EMAIL_TEMPLATE = '''
Hello {user_name},

You requested a password reset for your Hop & Barley account.

To reset your password, please click the following link:
{reset_url}

This link will be valid for 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
Hop & Barley Team
'''

# Messages
MESSAGES = {
    # Login messages
    'login_success': 'Successfully logged in!',
    'login_error': 'Invalid email or password. Please try again.',
    'logout_success': 'Successfully logged out!',

    # Profile messages
    'profile_updated': 'Profile updated successfully!',
    'profile_errors': 'Please correct the errors below.',

    # Password change messages
    'password_changed': 'Password changed successfully!',
    'password_errors': 'Please correct the errors below.',

    # Password reset messages
    'password_reset_sent': ('Password reset instructions have been sent to '
                            'your email.'),
    'password_reset_email_failed': ('Failed to send email. Please try again '
                                    'later.'),
    'password_reset_sent_generic': ('If an account with this email exists, '
                                    'password reset instructions have been '
                                    'sent.'),
    'password_reset_no_session': ('No password reset session found. Please '
                                  'request a new password reset.'),
    'password_reset_expired': ('Password reset session has expired. Please '
                               'request a new password reset.'),
    'password_reset_invalid_session': 'Invalid reset session.',
    'password_reset_success': ('Your password has been reset successfully. '
                               'You can now log in with your new password.'),
}

# Console logging templates
CONSOLE_LOGS = {
    'password_reset_email_sent': '''
==================================================
PASSWORD RESET EMAIL SENT
==================================================
To: {email}
Subject: {subject}
Reset URL: {reset_url}
User: {username} (ID: {user_id})
Session stored for user ID: {user_id}
Reset valid until: {valid_until}
==================================================
''',
    'password_reset_email_failed': '''
==================================================
EMAIL SENDING FAILED
==================================================
Error: {error}
To: {email}
==================================================
''',
    'password_reset_user_not_found': '''
==================================================
PASSWORD RESET REQUEST - USER NOT FOUND
==================================================
Email: {email}
Note: User not found in database
==================================================
''',
    'password_reset_no_session': '''
==================================================
PASSWORD RESET - NO SESSION DATA
==================================================
No valid reset session found
==================================================
''',
    'password_reset_session_expired': '''
==================================================
PASSWORD RESET - SESSION EXPIRED
==================================================
Session timestamp: {session_time}
Current time: {current_time}
Time difference: {time_diff:.1f} minutes
==================================================
''',
    'password_reset_attempt': '''
==================================================
PASSWORD RESET ATTEMPT
==================================================
User: {username} (ID: {user_id})
Email: {email}
Session valid until: {valid_until}
==================================================
''',
    'password_reset_user_not_found_session': '''
==================================================
PASSWORD RESET - USER NOT FOUND
==================================================
User ID: {user_id}
Email: {email}
==================================================
''',
    'password_reset_successful': '''
==================================================
PASSWORD RESET SUCCESSFUL
==================================================
User: {username} (ID: {user_id})
Email: {email}
Password updated successfully
Reset session cleared
==================================================
''',
}
