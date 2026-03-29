# ============================================================
# File: users/decorators.py
# Django Event Management System — Custom Access Decorators
# Skills Applied: django-backend + owasp-security
# ============================================================

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def staff_required(view_func):
    """
    Decorator that requires the user to be logged in AND have is_staff=True.
    Non-staff users are redirected to home with an error message.
    Satisfies owasp-security rule: admin pages need is_staff=True.
    Usage: @staff_required on any admin/dashboard view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('account_login')
        # Then check staff status
        if not request.user.is_staff and not request.user.is_admin_user():
            messages.error(
                request,
                "Access denied. You need admin privileges to view this page."
            )
            return redirect('events:event_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def anonymous_required(redirect_url='/'):
    """
    Decorator that redirects logged-in users away from auth pages.
    Prevents logged-in users from accessing /login or /register.
    Usage: @anonymous_required() on login and register views.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
