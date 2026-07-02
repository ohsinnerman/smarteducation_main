"""Development settings. Convenient defaults; nothing here is required."""

from .base import *  # noqa: F401,F403
from .base import config

# Default DEBUG on in dev unless explicitly overridden.
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)

# Warn loudly (not fatally) about optional integrations that are unset, so a
# missing key is visible immediately instead of discovered three weeks later.
from .checks import warn_optional_integrations  # noqa: E402

warn_optional_integrations(globals())
