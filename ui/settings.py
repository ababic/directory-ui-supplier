"""
Django settings for ui project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DEBUG", False))

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    "django_extensions",
    "raven.contrib.django.raven_compat",
    "django.contrib.sessions",
    "formtools",
    "ui",
    "enrolment",
    "user",
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sso.middleware.SSOUserMiddleware',
    'enrolment.middleware.ReferrerMiddleware',
]

ROOT_URLCONF = 'ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'sso.context_processors.sso_user_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ui.wsgi.application'


# # Database
# hard to get rid of this
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'LOCATION': 'unique-snowflake',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# directory-api
API_CLIENT_BASE_URL = os.environ["API_CLIENT_BASE_URL"]
API_CLIENT_KEY = os.environ["API_CLIENT_KEY"]

# directory-sso
SSO_API_CLIENT_BASE_URL = os.environ["SSO_API_CLIENT_BASE_URL"]
SSO_API_CLIENT_KEY = os.environ["SSO_API_CLIENT_KEY"]
SSO_LOGIN_URL = os.environ["SSO_LOGIN_URL"]
SSO_LOGOUT_URL = os.environ["SSO_LOGOUT_URL"]
SSO_SIGNUP_URL = os.environ["SSO_SIGNUP_URL"]
SSO_REDIRECT_FIELD_NAME = os.environ["SSO_REDIRECT_FIELD_NAME"]
SSO_SESSION_COOKIE = os.environ["SSO_SESSION_COOKIE"]

ANALYTICS_ID = os.getenv("ANALYTICS_ID")

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Sentry
RAVEN_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN"),
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true') == 'true'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

VALIDATOR_MAX_LOGO_SIZE_BYTES = int(os.getenv(
    "VALIDATOR_MAX_LOGO_SIZE_BYTES", 10 * 1024 * 1024
))

COMPANIES_HOUSE_SEARCH_URL = os.environ["COMPANIES_HOUSE_SEARCH_URL"]

FEEDBACK_FORM_URL = os.environ['FEEDBACK_FORM_URL']
