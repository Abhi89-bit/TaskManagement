"""
WSGI config for tastmanagement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import sys
import os

# Set the correct path to your project
path = '/home/yourusername/TaskManagement'
if path not in sys.path:
    sys.path.append(path)

# Activate virtual environment
venv_path = '/home/yourusername/TaskManagement/venv/bin/activate_this.py'
with open(venv_path) as f:
    exec(f.read(), dict(__file__=venv_path))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TaskManagement.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
