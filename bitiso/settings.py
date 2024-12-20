import os
import sys
from dotenv import load_dotenv
load_dotenv()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'torrents': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tracker_scraper': {  # Suppress unnecessary warnings
            'handlers': ['console'],
            'level': 'ERROR',  # Only log ERROR or higher from tracker_scraper
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


"""
Django settings for bitiso project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change_me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')


# Application definition

INSTALLED_APPS = [
    'modeltranslation', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'rosetta',
    'core.accounts',
    'core.pages',
    'core.user_profiles',
    'bitiso_user_profiles',
    'torrents',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bitiso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [BASE_DIR / 'templates'],  # This tells Django where to look for global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                 # Add the custom project name context processor
                'bitiso.context_processors.project_name',
                'bitiso.context_processors.page_list',
                'bitiso.context_processors.profile_user',
                'bitiso.context_processors.use_uuid_for_profile_url', 
                'bitiso.context_processors.user_dashboard_counts', 
                'bitiso.context_processors.gtag_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'bitiso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

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

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'UTC')

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'), 
]

# MODELTRANSLATION_FALLBACK_LANGUAGES = {
#     'default': ('en',),  # Default fallback to English
# }

# Path to translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'accounts/locale'),
]

# webroot
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBROOT = os.getenv('DJANGO_WEBROOT_PATH', os.path.join(BASE_DIR, 'webroot'))

# static
STATIC_URL = os.getenv('DJANGO_STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', os.path.join(WEBROOT, 'static'))
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "core/static",  # Ensure the path is correct
]

# media
MEDIA_URL = os.getenv('DJANGO_MEDIA_URL', '/media/')
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT', os.path.join(WEBROOT, 'media'))

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Custom User Model 
AUTH_USER_MODEL = 'accounts.CustomUser'

# Redirect when logout
LOGOUT_REDIRECT_URL = '/'

# Redirect when login
LOGIN_REDIRECT_URL = '/'

# Use UUID or Username in URLs
USE_UUID_FOR_PROFILE_URL = True  # Set to False to use username

# Time limit for changing username (in days)
USERNAME_CHANGE_LIMIT_DAYS = 1  # Set the limit for changing usernames (e.g., 7 days)

PROJECT_NAME = os.getenv('PROJECT_NAME ','Project')

# settings.py
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST ','smtp@localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT ','587')
EMAIL_USE_TLS = os.getenv('EMAIL_TLS ','True')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','login')  # Your email address
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','login')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL','noreply@noreply.com')

EMAIL_VERIFICATION_REQUIRED = False

# MODELTRANSLATION_TRANSLATION_FILES = (
#     'pages.translation',  # Path to your translation.py file
# )

COPYRIGHT_START_YEAR = 2018


#MEDIA_URL = '/media/'  # URL to serve media files
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Absolute filesystem path to media directory

#MEDIA_TORRENT = os.path.join(MEDIA_ROOT, 'torrents/')
MEDIA_TORRENT = os.getenv('MEDIA_TORRENT', os.path.join(WEBROOT, 'torrents'))

raw_trackers = os.getenv('TRACKER_ANNOUNCE', '')
TRACKER_ANNOUNCE = [tracker.strip() for tracker in raw_trackers.split(',') if tracker.strip()]


MAX_FILE_SIZE_MB = 10


# Google Tag Manager
GTAG_ENABLE = os.getenv('GTAG_ENABLE', 'False') == 'True'
GTAG_ID = os.getenv('GTAG_ID', '')

# Pagination 

PAGINATION_COUNT = os.getenv('PAGINATION_COUNT', '20')
