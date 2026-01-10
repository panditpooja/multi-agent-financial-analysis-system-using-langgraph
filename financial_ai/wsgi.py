"""
WSGI config for Financial AI project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_ai.settings')

application = get_wsgi_application()

