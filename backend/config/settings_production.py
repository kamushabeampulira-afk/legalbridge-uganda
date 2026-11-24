"""
LegalBridge — Production settings override.
Import base settings then override for production.

Usage: set DJANGO_SETTINGS_MODULE=config.settings_production
"""
from .settings import *  # noqa
from .settings import env  # noqa — re-export env for use below

import os

DEBUG = False

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['legalbridgeug.org', 'api.legalbridgeug.org'])

# Render exposes the service at <name>.onrender.com in addition to any custom
# domains. Add it automatically so health checks and the public URL work even
# before custom-domain DNS is configured.
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

# ── Security ──────────────────────────────────────────────────────────────────
# Render terminates TLS at the edge and forwards plain HTTP with this header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
# The platform health probe calls /healthz over plain HTTP; do not redirect it.
SECURE_REDIRECT_EXEMPT = [r'^healthz$']
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ── Redis Cache (USSD sessions + general caching) ────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
    }
}

# ── Static files ─────────────────────────────────────────────────────────────
# Django 5 uses STORAGES; STATICFILES_STORAGE would conflict with the base
# setting and abort startup. WhiteNoise is already configured there.
STORAGES = dict(STORAGES)
STORAGES['staticfiles'] = {
    'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'legalbridge': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
