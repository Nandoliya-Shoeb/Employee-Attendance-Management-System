# ============================================================
# File: users/urls.py
# Django Event Management System — Users App URL Configuration
# ============================================================

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User profile page (Step 2 will fill these out)
    path('profile/', views.profile_view, name='profile'),
]
