"""
WSGI config for tastmanagement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import os
import sys

# Set the correct path to your Django project
path = '/home/Abhiraj18/TaskManagement'
if path not in sys.path:
    sys.path.append(path)

# Activate virtual environment
venv_path = '/home/Abhiraj18/TaskManagement/venv/bin/activate_this.py'
if os.path.exists(venv_path):
    with open(venv_path) as f:
        exec(f.read(), dict(__file__=venv_path))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TaskManagement.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
