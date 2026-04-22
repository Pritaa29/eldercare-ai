"""
WSGI config for eldercare project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

"""
WSGI config for ElderCare AI project.
For production, use Daphne (ASGI) instead for WebSocket support.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eldercare.settings')
application = get_wsgi_application()