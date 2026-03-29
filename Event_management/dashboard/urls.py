# ============================================================
# File: dashboard/urls.py
# Django Event Management System — Dashboard App URLs
# ============================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Admin dashboard (Step 5 will fill these out)
    path('', views.dashboard_home, name='home'),
]
