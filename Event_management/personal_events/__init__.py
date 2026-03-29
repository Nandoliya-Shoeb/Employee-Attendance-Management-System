# ============================================================
# File: personal_events/__init__.py
# Django Event Management System
# Load Celery app when Django starts
# ============================================================

# Import Celery app so it initializes when Django starts.
# This ensures @shared_task decorators work correctly.
from .celery import app as celery_app

__all__ = ('celery_app',)
