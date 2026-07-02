"""
Up-front configuration checks for the notification integrations.

Each sender calls its check first so a *configuration* problem (missing creds) is
logged clearly and distinctly, instead of failing deep inside the Twilio/SMTP SDK
with a confusing stack trace or being silently recorded as a generic delivery
"failed". Returns (ok: bool, reason: str).
"""

import logging

from django.conf import settings

logger = logging.getLogger("smarteducation.notifications")


def email_configured():
    if not (settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD):
        reason = "EMAIL_HOST_USER/EMAIL_HOST_PASSWORD not set"
        logger.warning("Email notification skipped: %s.", reason)
        return False, reason
    return True, ""


def twilio_configured():
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER):
        reason = "TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN/TWILIO_PHONE_NUMBER not set"
        logger.warning("Twilio (SMS/WhatsApp) notification skipped: %s.", reason)
        return False, reason
    return True, ""
