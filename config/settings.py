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
        'NAME': ('django.contrib.auth.password_validation.'
                 'UserAttributeSimilarityValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'MinimumLengthValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'CommonPasswordValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'NumericPasswordValidator'),
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

# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@hopandbarley.com'

# Email templates
PASSWORD_RESET_EMAIL_SUBJECT = 'Password Reset - Hop & Barley'
PASSWORD_RESET_EMAIL_TEMPLATE = """
Hello {user_name},

You requested a password reset for your Hop & Barley account.

To reset your password, please click the following link:
{reset_url}

This link will be valid for 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
Hop & Barley Team
"""

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
    'password_reset_email_sent': """
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
""",
    'password_reset_email_failed': """
==================================================
EMAIL SENDING FAILED
==================================================
Error: {error}
To: {email}
==================================================
""",
    'password_reset_user_not_found': """
==================================================
PASSWORD RESET REQUEST - USER NOT FOUND
==================================================
Email: {email}
Note: User not found in database
==================================================
""",
    'password_reset_no_session': """
==================================================
PASSWORD RESET - NO SESSION DATA
==================================================
No valid reset session found
==================================================
""",
    'password_reset_session_expired': """
==================================================
PASSWORD RESET - SESSION EXPIRED
==================================================
Session timestamp: {session_time}
Current time: {current_time}
Time difference: {time_diff:.1f} minutes
==================================================
""",
    'password_reset_attempt': """
==================================================
PASSWORD RESET ATTEMPT
==================================================
User: {username} (ID: {user_id})
Email: {email}
Session valid until: {valid_until}
==================================================
""",
    'password_reset_user_not_found_session': """
==================================================
PASSWORD RESET - USER NOT FOUND
==================================================
User ID: {user_id}
Email: {email}
==================================================
""",
    'password_reset_successful': """
==================================================
PASSWORD RESET SUCCESSFUL
==================================================
User: {username} (ID: {user_id})
Email: {email}
Password updated successfully
Reset session cleared
==================================================
""",
}
