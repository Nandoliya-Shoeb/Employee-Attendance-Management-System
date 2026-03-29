# ============================================================
# File: events/urls.py
# Django Event Management System — Events App URL Configuration
# ============================================================

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Homepage — event listing (Step 3 will fill these out)
    path('', views.event_list, name='event_list'),
]
