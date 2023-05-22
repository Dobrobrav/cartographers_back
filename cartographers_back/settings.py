"""
Django settings for cartographers_back project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import dj_database_url
import redis

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qi)bm+ds$@qc%a-287gg09xm#27w3z(wki-5xzfb&=yma7^132'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_selectel_storage',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',

    'foo_app',
    'rooms',
    'games.apps.GamesConfig',
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

ROOT_URLCONF = 'cartographers_back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'cartographers_back.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

EXTERNAL_POSTGRES_URL = 'postgres://user:ukfvSVC8RC73GY1Nhhp52WVjUGMr26u3@dpg-chfrl9jhp8u065ri1lig-a.oregon-postgres.render.com/cartographers'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cartographers',
        'USER': 'postgres',
        'PASSWORD': '1771',
        'HOST': 'postgres',
        # 'HOST': 'localhost',
        'PORT': 5432,
        # 'PORT': 5433,
    },

    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'cartographers',
    #     'USER': 'user',
    #     'PASSWORD': 'ukfvSVC8RC73GY1Nhhp52WVjUGMr26u3',
    #     'HOST': 'postgres.render.com',
    #     'PORT': '5432',
    # }

    # 'default': dj_database_url.config(default=EXTERNAL_POSTGRES_URL)

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

DEFAULT_FILE_STORAGE = 'django_selectel_storage.storage.SelectelStorage'

SELECTEL_STORAGES = {
    'default': {
        'USERNAME': '217742_cartographers',
        'PASSWORD': '_^lsosL087',
        'CONTAINER': 'cartographers',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

# AUTHTOKEN_TOKEN_LIFETIME = 24 * 60 * 60  # token lifespan is 24 hours

REDIS = redis.Redis(
    host='redis',
    # host='localhost',
    port=6379,
    # port=6380,
    db=0,
)

# поправить константу ниже
# REDIS_EXTERNAL_URL = ''
# REDIS = redis.from_url(
#     url='rediss://red-chhjm4l269v0od74i080:wORNIkK67CkWvDdU25n6BC0C5wYRE6N1@oregon-redis.render.com:6379'
# )
