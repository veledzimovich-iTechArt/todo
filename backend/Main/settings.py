"""
Django settings for Main project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import socket
import os
from dotenv import load_dotenv
from pathlib import Path

from celery.schedules import crontab

from django.utils.log import DEFAULT_LOGGING

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG"))

# this is the host that Docker uses to run application
ALLOWED_HOSTS = ['localhost', '0.0.0.0', 'api']
APPEND_SLASH = False

# Application definition
PROJECT_APPS = [
    # core app created for manage fixtures
    'core',
    'users',
    'cards'
]
DEBUG_APPS = [app for app in ["debug_toolbar"] if DEBUG]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # celery
    'celery',
    # rest
    'corsheaders',
    'rest_framework',
    # redis
    'django_redis',
    *DEBUG_APPS,
    *PROJECT_APPS
]

MIDDLEWARE = [
    # debug
    *[app for app in ["debug_toolbar.middleware.DebugToolbarMiddleware"] if DEBUG],
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # rest
    'corsheaders.middleware.CorsMiddleware',
    # before 'django.middleware.common.CommonMiddleware'
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'Main.urls'

# rest

# CORS_ALLOWED_ORIGINS should be list!
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:3000',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://0.0.0.0:3000',
]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'Main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'todo'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', 5432),
        'CONN_MAX_AGE': int(os.environ.get('DATABASE_CONN_MAX_AGE', 600))
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # pagination
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 8
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# redis
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = '6379'

REDIS_DEFAULT_CACHE_DB = '0'
REDIS_SESSION_DB = '1'
REDIS_LOGIN_ATTEMPTS_DB = '2'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DEFAULT_CACHE_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 60 * 24  # one day
    },
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_SESSION_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 60 * 24  # one day
    }
}

DISABLE_CACHE = False
if DISABLE_CACHE:
    CACHES['default'] = {
        'BACKEND': 'adlynx_core.cache.ExtendedDummyCache'
    }

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24

# Celery settings
REDIS_BROKER_DB = '2'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}'
# use json to prevent error with superuser
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_RESULT_EXPIRES = 360
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULE = {
    'notify_users': {
        'task': 'cards.tasks.notify_users',
        'schedule': crontab(minute='*/5')
    },
}

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z'
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'main-logfile': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_DIR, 'logs', 'Main.log'),
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 100,
            'formatter': 'verbose'
        },
        'celery-logfile': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_DIR, 'logs', 'celery.log'),
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 100,
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True
    },

    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'celery-warning': {
            'handlers': ['celery-logfile'],
            'level': 'WARNING',
            'propagate': False
        },
        'main-warning': {
            'handlers': ['main-logfile'],
            'level': 'WARNING',
            'propagate': False
        },
    }
}

# django-debug-toolbar
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1"
    ]
    # add django-debug-toolbar in docker
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
