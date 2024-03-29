"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os

from api.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test',
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', 5432),
        'CONN_MAX_AGE': int(os.environ.get('DATABASE_CONN_MAX_AGE', 600))
    }
}

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = {}

# Week pasword hasher to make tests faster
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
