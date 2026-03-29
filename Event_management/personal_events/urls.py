# ============================================================
# File: personal_events/urls.py
# Django Event Management System — Root URL Configuration
# Skills Applied: django-backend
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication (django-allauth handles login, register, verify email)
    path('accounts/', include('allauth.urls')),

    # App URLs (each app manages its own URL file)
    path('', include('events.urls')),               # Public event pages (homepage)
    path('users/', include('users.urls')),           # User profile
    path('registrations/', include('registrations.urls')),  # Registration flow
    path('dashboard/', include('dashboard.urls')),   # Admin dashboard

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'personal_events.views.error_404'
handler500 = 'personal_events.views.error_500'
