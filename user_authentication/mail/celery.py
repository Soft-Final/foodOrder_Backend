# project_name/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set to your Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodOrder_Backend.settings')

app = Celery('foodOrder_Backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
