# ============================================================
# File: registrations/urls.py
# Django Event Management System — Registrations App URLs
# ============================================================

from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    # Registration flow (Step 4 will fill these out)
    path('', views.registration_list, name='registration_list'),
]
