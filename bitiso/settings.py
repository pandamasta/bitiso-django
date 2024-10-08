import os
from dotenv import load_dotenv
load_dotenv()


"""
Django settings for bitiso project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change_me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'


ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Extra app attached to this project
extra_apps = os.getenv('DJANGO_EXTRA_APPS', '')
if extra_apps:
    extra_apps_list = extra_apps.split(',')
    INSTALLED_APPS.extend(extra_apps_list)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'torrent.middleware.RateLimitMiddleware',  # Add the rate-limiting middleware here

]

ROOT_URLCONF = 'bitiso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                 # Custom context processor
                'torrent.context_processors.gtag_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'bitiso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DJANGO_DB_ENGINE = os.getenv('DJANGO_DB_ENGINE', 'sqlite')

if DJANGO_DB_ENGINE == 'pgsql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DJANGO_DB_NAME', 'your_database_name'),
            'USER': os.getenv('DJANGO_DB_USER', 'your_username'),
            'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', 'your_password'),
            'HOST': os.getenv('DJANGO_DB_HOST', 'localhost'),
            'PORT': os.getenv('DJANGO_DB_PORT', '5432'),
        }
    }
else:  # Default to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'bitiso.sqlite',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# webroot
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBROOT = os.getenv('DJANGO_WEBROOT_PATH', os.path.join(BASE_DIR, 'webroot'))

# static
STATIC_URL = os.getenv('DJANGO_STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', os.path.join(WEBROOT, 'static'))

# media
MEDIA_URL = os.getenv('DJANGO_MEDIA_URL', '/media/')
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT', os.path.join(WEBROOT, 'media'))

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')

# GTAG
GTAG_ENABLE = os.getenv('GTAG_ENABLE', 'False') == 'True'
GTAG_ID = os.getenv('GTAG_ID', '')

# Rate limiting

ENABLE_RATE_LIMITING = False # Set to False to disable rate limiting


# APP - Bitiso env

TRACKER_ANNOUNCE = os.getenv('TORRENT_TRACKER_ANNOUNCE', '').split(',')

TORRENT_FILES = os.getenv('TORRENT_FILES', os.path.join(WEBROOT, 'torrent', 'media'))
ENFORCE_CREATE = os.getenv('ENFORCE_CREATE', 'True')

TORRENT_DATA_TMP = os.getenv('TORRENT_DATA_TMP', os.path.join(WEBROOT, 'torrent', 'data_tmp'))
TORRENT_DATA = os.getenv('TORRENT_DATA', os.path.join(WEBROOT, 'torrent', 'data'))

TORRENT_EXTERNAL = os.getenv('DJANGO_TORRENT_EXTERNAL', os.path.join(WEBROOT, 'torrent','external'))
BITISO_TORRENT_STATIC = os.getenv('BITISO_TORRENT_STATIC', os.path.join(WEBROOT, 'media', 'torrent'))

MEDIA_TORRENT = os.getenv('MEDIA_TORRENT', os.path.join(WEBROOT, 'media', 'torrent'))
