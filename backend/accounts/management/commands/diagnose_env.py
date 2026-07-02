"""
`python manage.py diagnose_env`

Prints which environment/config values are resolved and which optional
integrations are configured vs. missing. This is the permanent tool for catching
"works on my machine, blank on EC2" problems immediately — run it as part of the
deploy so a bad env is caught at deploy time, not discovered later when a feature
silently doesn't work.

Exit code is non-zero if a required-in-production value is missing while
DJANGO_ENV=production, so it can gate a deploy.
"""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from smarteducation.settings.checks import integration_status


REQUIRED_IN_PRODUCTION = [
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CORS_ALLOWED_ORIGINS",
]


def _mask(value):
    if not value:
        return "(not set)"
    s = str(value)
    if len(s) <= 6:
        return "***"
    return f"{s[:3]}…{s[-2:]} (len {len(s)})"


class Command(BaseCommand):
    help = "Report resolved configuration and which integrations are configured."

    def handle(self, *args, **options):
        env = getattr(settings, "ENVIRONMENT", "development")
        self.stdout.write(self.style.MIGRATE_HEADING(f"Environment: {env}"))
        self.stdout.write(f"  DEBUG                = {settings.DEBUG}")
        self.stdout.write(f"  ALLOWED_HOSTS        = {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"  CORS_ALLOWED_ORIGINS = {settings.CORS_ALLOWED_ORIGINS}")
        self.stdout.write(f"  SECRET_KEY           = {_mask(settings.SECRET_KEY)}")

        db = settings.DATABASES["default"]
        engine = db.get("ENGINE", "")
        self.stdout.write(
            f"  DATABASE             = {engine.rsplit('.', 1)[-1]} "
            f"@ {db.get('HOST') or 'local'} / {db.get('NAME')}"
        )
        if env == "production" and "sqlite" in engine:
            self.stdout.write(self.style.ERROR(
                "  !! SQLite in production — DATABASE_URL is not set correctly."
            ))

        self.stdout.write(self.style.MIGRATE_HEADING("\nOptional integrations:"))
        for name, (configured, message) in integration_status(settings).items():
            if configured:
                self.stdout.write(self.style.SUCCESS(f"  [ON]  {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  [OFF] {name} — {message}"))

        # Gate deploys: in production, missing required values is a failure.
        missing = []
        if env == "production":
            for attr in REQUIRED_IN_PRODUCTION:
                if not getattr(settings, attr, None):
                    missing.append(attr)
            if "sqlite" in engine:
                missing.append("DATABASE_URL")

        if missing:
            self.stdout.write(self.style.ERROR(
                f"\nMissing required production config: {', '.join(missing)}"
            ))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("\nEnvironment diagnosis complete."))
