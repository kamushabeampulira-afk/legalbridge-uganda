"""
LegalBridge Informal — Django Settings
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

# ---------------------------------------------------------
# Core
# ---------------------------------------------------------
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DJANGO_DEBUG', default=True)
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # LegalBridge apps
    'users',
    'documents',
    'legal_data',
    'ai_engine',
    'voice',
    'channels_app',
    'referrals',
    'analytics',
    'subscriptions',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
if env('DB_ENGINE', default='postgresql') == 'sqlite':
    # Local dev convenience: set DB_ENGINE=sqlite in .env to skip PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='legalbridge_db'),
            'USER': env('DB_USER', default='legalbridge_user'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }

# ---------------------------------------------------------
# Auth
# ---------------------------------------------------------
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------
# REST Framework
# ---------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '60/minute',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=env.int('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=30)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:8081', 'http://localhost:19006']
)
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------
# File Storage & Media
# ---------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MAX_UPLOAD_SIZE_MB = env.int('MAX_UPLOAD_SIZE_MB', default=10)
ALLOWED_DOCUMENT_TYPES = ['image/jpeg', 'image/png', 'application/pdf']

# ---------------------------------------------------------
# Localisation
# ---------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# AI / OpenAI
# ---------------------------------------------------------
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o')
OPENAI_TIMEOUT_SECONDS = env.float('OPENAI_TIMEOUT_SECONDS', default=60)
OPENAI_MAX_RETRIES = env.int('OPENAI_MAX_RETRIES', default=1)
OPENAI_HEALTHCHECK_TIMEOUT_SECONDS = env.float('OPENAI_HEALTHCHECK_TIMEOUT_SECONDS', default=20)
# A health-check response slower than this is reported as "working with warnings"
OPENAI_HEALTHCHECK_SLOW_MS = env.int('OPENAI_HEALTHCHECK_SLOW_MS', default=10000)
# Development only: return clearly-labelled placeholder text when no API key is set.
# Off by default so a missing key is reported as an error, never as an explanation.
AI_DEMO_MODE = env.bool('AI_DEMO_MODE', default=False)

# Legal sources verified longer ago than this are flagged as needing re-checking
LEGAL_SOURCE_MAX_AGE_DAYS = env.int('LEGAL_SOURCE_MAX_AGE_DAYS', default=365)

# ---------------------------------------------------------
# ChromaDB (RAG vector store)
# ---------------------------------------------------------
CHROMA_PERSIST_DIR = env('CHROMA_PERSIST_DIR', default=str(BASE_DIR / 'chroma_db'))
CHROMA_COLLECTION_NAME = env('CHROMA_COLLECTION_NAME', default='legalbridge_sources')

# ---------------------------------------------------------
# Africa's Talking (USSD)
# ---------------------------------------------------------
AT_USERNAME = env('AT_USERNAME', default='sandbox')
AT_API_KEY = env('AT_API_KEY', default='')
AT_SHORTCODE = env('AT_SHORTCODE', default='*384*0#')
AT_ENVIRONMENT = env('AT_ENVIRONMENT', default='sandbox')

# ---------------------------------------------------------
# Voice / TTS / STT
# ---------------------------------------------------------
TTS_PROVIDER = env('TTS_PROVIDER', default='openai')
ELEVENLABS_API_KEY = env('ELEVENLABS_API_KEY', default='')
ELEVENLABS_VOICE_EN = env('ELEVENLABS_VOICE_EN', default='')
ELEVENLABS_VOICE_LG = env('ELEVENLABS_VOICE_LG', default='')
STT_PROVIDER = env('STT_PROVIDER', default='openai_whisper')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Cache (dev uses LocMemCache; prod overrides with Redis) ───────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'legalbridge-ussd',
    }
}

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'legalbridge': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
