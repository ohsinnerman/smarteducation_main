"""
WSGI config for smarteducation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# The settings package selects development vs production internally based on
# DJANGO_ENV, so a single module name works in every environment.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarteducation.settings')

application = get_wsgi_application()
