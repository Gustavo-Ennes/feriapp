# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import environ
import io

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

env_file = os.path.join(BASE_DIR, ".env")

env = environ.Env()
# If no .env has been provided, pull it from Secret Manager
if os.path.isfile(env_file):
    env.read_env(env_file)
else:
    # Create local settings if running with CI, for unit testing
    if os.getenv("TRAMPOLINE_CI", None):
        placeholder = f"SECRET_KEY=a\nGS_BUCKET_NAME=none\nDATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
        env.read_env(io.StringIO(placeholder))
    else:
        # [START cloudrun_django_secretconfig]

        import google.auth
        from google.cloud import bigquery
        from google.cloud import secretmanager

        _, project = google.auth.default()

        if project:
            client = secretmanager.SecretManagerServiceClient()

            SETTINGS_NAME = os.environ.get("SETTINGS_NAME", "django_settings")
            name = f"projects/{project}/secrets/{SETTINGS_NAME}/versions/latest"
            payload = client.access_secret_version(name=name).payload.data.decode(
                "UTF-8"
            )
        env.read_env(io.StringIO(payload))
        # [END cloudrun_django_secretconfig]



# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here.
# See https://docs.djangoproject.com/en/1.10/ref/settings/
ALLOWED_HOSTS = ['*']

# Application definition

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'sass_processor',
    'crispy_forms',
    'app',
    'compressor',
    'django_user_agents',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]


ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'mysite/templates/'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# [START db_setup]
if not DEBUG:
# if os.getenv('GAE_APPLICATION', None):
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'feriapp',
            'CLIENT': {
                'host': os.getenv('DB_STRING')
            },   
            'ENFORCE_SCHEMA': False

        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'feriapp_test',
            'CLIENT': {
                'host': os.getenv('DB_TEST_STRING')
            },   
            'ENFORCE_SCHEMA': False

        }
    }
# [END


# Use a in-memory sqlite3 database when testing in CI systems
if os.getenv('TRAMPOLINE_CI', None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
        }
    }




LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(BASE_DIR, 'scss'),
    os.path.join(BASE_DIR, 'threejs')
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
    "compressor.finders.CompressorFinder",
]


COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

SASS_PROCESSOR_ROOT = STATIC_ROOT
SASS_PRECISION = 8
SASS_OUTPUT_STYLE = 'compact'


LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = "index"


CRISPY_TEMPLATE_PACK = 'bootstrap4'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] '
                       'pathname=%(pathname)s lineno=%(lineno)s '
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

#sessão durará 10 horas
SESSION_COOKIE_AGE = 60 * 60 * 10

DEBUG_PROPAGATE_EXCEPTIONS = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

# [START cloudrun_django_staticconfig]
# Define static storage via django-storages[google]
GS_BUCKET_NAME = 'feriapp'

DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"
# [END cloudrun_django_staticconfig]

