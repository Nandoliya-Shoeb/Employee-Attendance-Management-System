# ============================================================
# File: personal_events/settings.py
# Django Event Management System — Full Settings Configuration
# Skills Applied: django-backend + database-design + owasp-security
# ============================================================

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------
# SECURITY — owasp-security skill
# ----------------------------------------------------------
# Never hardcode SECRET_KEY — always read from .env
SECRET_KEY = config('SECRET_KEY')

# Read DEBUG from .env (False in production)
DEBUG = config('DEBUG', default=False, cast=bool)

# Comma-separated list of allowed hosts from .env
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# ----------------------------------------------------------
# APPLICATIONS
# ----------------------------------------------------------
INSTALLED_APPS = [
    # Django Built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-Party Apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_htmx',
    'axes',                     # Login attempt limiting (owasp-security)
    'django_celery_results',
    'django_celery_beat',

    # Our Apps
    'users',
    'events',
    'registrations',
    'dashboard',
]

# ----------------------------------------------------------
# MIDDLEWARE — owasp-security: axes must be after auth
# ----------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    # Static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',     # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'axes.middleware.AxesMiddleware',               # Must be last auth-related
]

ROOT_URLCONF = 'personal_events.urls'

# ----------------------------------------------------------
# TEMPLATES
# ----------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],           # Global templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'personal_events.wsgi.application'

# ----------------------------------------------------------
# DATABASE — database-design skill: PostgreSQL only
# ----------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# ----------------------------------------------------------
# AUTHENTICATION — owasp-security skill
# ----------------------------------------------------------
# Use our custom User model (defined in Step 2)
AUTH_USER_MODEL = 'users.CustomUser'

# django-allauth configuration
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',          # Brute-force protection
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# allauth settings — owasp-security: mandatory email verification
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5              # owasp: 5 attempts max
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300          # 5 minutes lockout
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'

# ----------------------------------------------------------
# PASSWORD VALIDATION — owasp-security skill
# ----------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------------------------
# SESSION SECURITY — owasp-security skill
# Session timeout: 30 minutes of inactivity
# ----------------------------------------------------------
SESSION_COOKIE_AGE = 1800                           # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True                   # Reset timer on activity
SESSION_COOKIE_HTTPONLY = True                      # No JS access to cookie
SESSION_COOKIE_SAMESITE = 'Lax'

# ----------------------------------------------------------
# DJANGO-AXES — Brute Force Protection (owasp-security)
# 5 failed logins → 5 min lockout
# ----------------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.08333                         # 5 minutes in hours
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'users/lockout.html'

# ----------------------------------------------------------
# INTERNATIONALIZATION
# ----------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------
# STATIC & MEDIA FILES — django-backend skill
# ----------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise for production static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------------------------------------
# EMAIL CONFIGURATION — All values from .env
# ----------------------------------------------------------
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='EventHub <noreply@eventhub.com>')

# ----------------------------------------------------------
# CELERY CONFIGURATION — Task Queue
# ----------------------------------------------------------
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_TASK_TRACK_STARTED = True

# ----------------------------------------------------------
# RAZORPAY — Payment Gateway (keys from .env)
# ----------------------------------------------------------
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# ----------------------------------------------------------
# SITE CONFIGURATION
# ----------------------------------------------------------
SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')
SITE_NAME = config('SITE_NAME', default='EventHub')

# ----------------------------------------------------------
# CRISPY FORMS
# ----------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ----------------------------------------------------------
# SECURITY HEADERS (Production) — owasp-security skill
# ----------------------------------------------------------
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
