"""
WSGI config for studentgov project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentgov.settings')

application = get_wsgi_application()

# --- Emergency Admin Creator ---
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Check if 'admin' already exists so it doesn't try to create it twice
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'earist_sslg_2026')
        print("Master Admin Created Successfully!")
except Exception as e:
    print(f"Admin creation error: {e}")
