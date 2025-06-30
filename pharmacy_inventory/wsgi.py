"""
WSGI config for pharmacy_inventory project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_inventory.settings')

application = get_wsgi_application()
