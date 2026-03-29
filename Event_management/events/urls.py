# ============================================================
# File: events/urls.py
# Django Event Management System — Events App URL Configuration
# ============================================================

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # ── Public URLs ──────────────────────────────────────────
    path('', views.event_list, name='event_list'),                          # Homepage
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),   # Detail page
    path('categories/', views.event_categories, name='categories'),         # Browse categories

    # ── Admin CRUD URLs ───────────────────────────────────────
    path('manage/events/', views.event_manage_list, name='manage_list'),    # Admin list
    path('manage/events/create/', views.event_create, name='create'),       # Create event
    path('manage/events/<slug:slug>/edit/', views.event_edit, name='edit'), # Edit event
    path('manage/events/<slug:slug>/delete/', views.event_delete, name='delete'),  # Delete
]
