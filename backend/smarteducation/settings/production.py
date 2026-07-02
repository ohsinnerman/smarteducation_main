"""
Production settings.

Hard rule: required configuration must come from the environment. If any of the
required vars is missing we raise at startup (ImproperlyConfigured) rather than
silently falling back to a dev default on a real server. Optional integrations
(email/Twilio/OpenAI) may be unset, but we log a loud, specific warning for each.
"""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import (  # noqa: E402
    BASE_DIR, config, MIDDLEWARE, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS,
)
from .base import Csv  # noqa: E402
import dj_database_url  # noqa: E402

DEBUG = False

# --- Required-in-production config: fail loudly if missing -----------------
_REQUIRED = ["DJANGO_SECRET_KEY", "DATABASE_URL", "DJANGO_ALLOWED_HOSTS", "CORS_ALLOWED_ORIGINS"]
_missing = []
for _var in _REQUIRED:
    try:
        _val = config(_var)
    except Exception:
        _val = ""
    if not _val:
        _missing.append(_var)
if _missing:
    raise ImproperlyConfigured(
        "Missing required production environment variable(s): "
        + ", ".join(_missing)
        + ". These are not optional in production and must not fall back to a dev "
        "default. Set them (see .env.example) or run `python manage.py diagnose_env`."
    )

SECRET_KEY = config("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", cast=Csv())
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())

# DATABASE_URL is required above, so no SQLite fallback can apply here.
DATABASES = {
    'default': dj_database_url.parse(config("DATABASE_URL"), conn_max_age=600),
}

# whitenoise for static serving behind gunicorn.
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    _sec = 'django.middleware.security.SecurityMiddleware'
    MIDDLEWARE = [_sec, 'whitenoise.middleware.WhiteNoiseMiddleware'] + [
        m for m in MIDDLEWARE if m != _sec
    ]

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Standard production security hardening.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Optional integrations: warn, don't fail.
from .checks import warn_optional_integrations  # noqa: E402

warn_optional_integrations(globals())
