"""
Shared startup checks for optional integrations.

Rather than let email/Twilio/OpenAI silently no-op when their credentials are
unset, we log a loud, specific warning naming exactly which integration is
disabled and why. This runs at settings-load time (called with the settings
module's own globals, since django.conf.settings isn't ready mid-import), and the
same map is reused by the `diagnose_env` management command.
"""

import logging

logger = logging.getLogger("smarteducation.env")

# name -> (list of setting attrs that must all be truthy, human message when off)
OPTIONAL_INTEGRATIONS = {
    "Email (SMTP)": (
        ["EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"],
        "email notifications are DISABLED",
    ),
    "Twilio (SMS/WhatsApp)": (
        ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"],
        "SMS and WhatsApp notifications are DISABLED",
    ),
    "OpenAI": (
        ["OPENAI_API_KEY"],
        "AI-generated insights fall back to canned text",
    ),
}


def integration_status(source):
    """Return {name: (configured, message)} given a dict-like settings source.

    `source` may be a settings-module globals() dict or the django settings
    object (anything supporting attribute or item access via _get).
    """
    def _get(key):
        if isinstance(source, dict):
            return source.get(key, "")
        return getattr(source, key, "")

    status = {}
    for name, (attrs, message) in OPTIONAL_INTEGRATIONS.items():
        configured = all(_get(a) for a in attrs)
        status[name] = (configured, message)
    return status


def warn_optional_integrations(source):
    """Emit a WARNING for each optional integration not configured in `source`."""
    for name, (configured, message) in integration_status(source).items():
        if not configured:
            attrs = OPTIONAL_INTEGRATIONS[name][0]
            logger.warning(
                "%s not configured (%s not set) — %s.",
                name, "/".join(attrs), message,
            )
