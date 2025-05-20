# car_sales/settings.py

import os
from pathlib import Path
from datetime import timedelta

# ──────────────────────────────────────────────────────────────────────────────
# BASE_DIR
# ──────────────────────────────────────────────────────────────────────────────
# BASE_DIR points to the root Ml-service-backend folder
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY = 'your-secret-key'      # ← replace with your real secret
DEBUG = False                       # ← turn off in production!
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '103.50.205.86',                # ← your server IP
]

APPEND_SLASH = False

# ──────────────────────────────────────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',   # <-- needed for admin + static

    # Third-party
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # Your apps
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'car_sales.urls'
WSGI_APPLICATION = 'car_sales.wsgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     'car',
        'USER':     'UserService',
        'PASSWORD': 'User@Service',
        'HOST':     '103.50.205.86',
        'PORT':     '5432',
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# TEMPLATES (needed for admin)
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':    [BASE_DIR / 'templates'],  # optional, if you have custom templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # required by admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
# Where `collectstatic` will gather all files
STATIC_ROOT = BASE_DIR / 'staticfiles'
# If you have a `static/` folder for your own assets, create it:
#   mkdir -p /home/cloudmn/Ml-service-backend/static
# You can remove this line if you don't use a static folder.
STATICFILES_DIRS = [BASE_DIR / 'static']

# ──────────────────────────────────────────────────────────────────────────────
# CORS / CSRF
# ──────────────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://103.50.205.86:3000",    # if you host a frontend on this IP:port
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://103.50.205.86:3000",
]

# ──────────────────────────────────────────────────────────────────────────────
# REST FRAMEWORK & JWT
# ──────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':       timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME':      timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':       True,
    'BLACKLIST_AFTER_ROTATION':    True,
    'AUTH_HEADER_TYPES':           ('Bearer',),
}

# ──────────────────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

