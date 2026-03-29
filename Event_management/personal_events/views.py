# ============================================================
# File: personal_events/views.py
# Django Event Management System — Custom Error Views
# Skills Applied: django-backend
# ============================================================

from django.shortcuts import render


def error_404(request, exception):
    """Render custom 404 Not Found page."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Render custom 500 Internal Server Error page."""
    return render(request, 'errors/500.html', status=500)
