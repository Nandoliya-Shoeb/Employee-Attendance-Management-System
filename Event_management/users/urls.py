# ============================================================
# File: users/urls.py
# Django Event Management System — Users App URL Configuration
# Skills Applied: django-backend
# ============================================================

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User registration (allauth handles login/logout, we add register)
    path('register/', views.register_view, name='register'),

    # User profile — view and edit
    path('profile/', views.profile_view, name='profile'),

    # Logout
    path('logout/', views.logout_view, name='logout'),

    # Remove profile picture
    path('profile/delete-avatar/', views.delete_avatar_view, name='delete_avatar'),
]
