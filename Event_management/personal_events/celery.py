# ============================================================
# File: personal_events/celery.py
# Django Event Management System — Celery App Configuration
# Skills Applied: django-backend
# ============================================================

import os
from celery import Celery

# Set default Django settings module for Celery worker
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_events.settings')

# Create Celery application instance
app = Celery('personal_events')

# Read Celery config from Django settings (CELERY_ prefix)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps (looks for tasks.py)
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working correctly."""
    print(f'Request: {self.request!r}')
