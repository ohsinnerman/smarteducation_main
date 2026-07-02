"""
Settings package entry point.

Selects the environment-specific settings module based on DJANGO_ENV
(development by default, production when DJANGO_ENV=production) so that a single
DJANGO_SETTINGS_MODULE=smarteducation.settings works everywhere — manage.py,
wsgi, asgi, celery, Docker, and EC2 — instead of each entry point choosing a
different module (the old settings.py vs production.py split).
"""

import os

from decouple import Config, RepositoryEnv
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_env_file = _BASE_DIR / ".env"
if _env_file.exists():
    _config = Config(RepositoryEnv(str(_env_file)))
    _env = _config("DJANGO_ENV", default="development")
else:
    _env = os.environ.get("DJANGO_ENV", "development")

if _env == "production":
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403
