"""Minimal Django settings for the django-statsd test suite."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ALLOWED_HOSTS = ['testserver']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
DEBUG = True
INSTALLED_APPS = ['django_statsd']
MIDDLEWARE = [
    'django_statsd.middleware.StatsdMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django_statsd.middleware.StatsdMiddlewareTimer',
]
ROOT_URLCONF = 'tests.urls'
SECRET_KEY = 'insecure-test-only-secret-key'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {},
    },
]
USE_TZ = True

STATSD_PREFIX = 'prefix'
STATSD_TRACK_MIDDLEWARE = True
