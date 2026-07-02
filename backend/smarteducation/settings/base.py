"""
Base Django settings shared by all environments.

Environment-specific overrides live in development.py / production.py, selected
by smarteducation/settings/__init__.py based on DJANGO_ENV.

Config loading: we pin python-decouple to an explicit .env path
(BASE_DIR / '.env') rather than relying on decouple's auto-discovery. Auto-
discovery searches from the current working directory, which differs between
local dev, Docker WORKDIR, and a systemd service on EC2 — so it would silently
find no .env and fall through to every `default=`. Pinning the path makes env
loading behave identically no matter where the process is started.
"""

from datetime import timedelta
from pathlib import Path

from decouple import Config, RepositoryEnv, Csv, UndefinedValueError

# BASE_DIR is the repo root (…/smarteducation), two levels up from this file:
# settings/base.py -> settings/ -> smarteducation/ -> <repo root>
BASE_DIR = Path(__file__).resolve().parent.parent.parent

_env_file = BASE_DIR / ".env"
if _env_file.exists():
    config = Config(RepositoryEnv(str(_env_file)))
else:
    # No .env on disk (e.g. env vars injected by Docker/systemd/CI). Fall back to
    # process environment only. This still fails loudly for required prod vars via
    # the checks in production.py.
    from decouple import config  # noqa: F401  (reads os.environ)

ENVIRONMENT = config("DJANGO_ENV", default="development")

SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-znkn3tz7r9zs$gur)59k3m7@moq^6s&)3!$93zv*#1_x19-r3l",
)

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',

    # Local apps
    'accounts',
    'students',
    'dashboards',
    'ml',
    'notifications',
    'api',
    'advanced_features',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CorsMiddleware must be as high as possible, before CommonMiddleware.
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smarteducation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'smarteducation.context_processors.global_template_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'smarteducation.wsgi.application'

# Database
# Single source of truth: DATABASE_URL. When unset, fall back to local SQLite.
# production.py hard-fails if DATABASE_URL is missing, so this fallback only ever
# applies to development.
import dj_database_url  # noqa: E402

DATABASES = {
    'default': dj_database_url.parse(
        config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Redirect settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # JWT first: a separately-hosted frontend can't rely on session cookies
        # across origins. Session auth kept for the Django admin / same-origin.
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=1, cast=int)
    ),
}

# CORS — origins come from env, never hardcoded / never "*".
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Twilio (SMS & WhatsApp)
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER", default="")

# Celery / Redis — read from env (CELERY_BROKER_URL, falling back to REDIS_URL).
_redis_url = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=_redis_url)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=_redis_url)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# AI/ML
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")

# Demo seeding: gate the post_migrate demo-account creation so it never runs
# silently against a real production database. (Consumed in accounts/signals.py;
# wired in Phase 2.)
SEED_DEMO_ACCOUNTS_ON_MIGRATE = config(
    "SEED_DEMO_ACCOUNTS_ON_MIGRATE", default=False, cast=bool
)
