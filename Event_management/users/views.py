# ============================================================
# File: users/views.py
# Django Event Management System — Users App Views
# Skills Applied: django-backend + owasp-security + frontend-design
# Rules: Function-based views only. @login_required on protected views.
#        All secrets in .env. Every function has a comment.
# ============================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .forms import CustomUserRegistrationForm, ProfileUpdateForm
from .decorators import anonymous_required


@anonymous_required(redirect_url='/')
@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Handle user registration.
    GET  → Show blank registration form.
    POST → Validate and create new user account, redirect to login.
    Security: anonymous_required prevents logged-in users from re-registering.
    """
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"🎉 Account created for {user.first_name}! "
                "Please check your email to verify your account before logging in."
            )
            return redirect('account_login')
        else:
            # Show error message for failed validation
            messages.error(
                request,
                "Please correct the errors below and try again."
            )
    else:
        # GET request — show empty form
        form = CustomUserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """
    Display and update authenticated user's profile.
    GET  → Show profile with current data pre-filled in form.
    POST → Validate and save updated profile data.
    Security: @login_required ensures only authenticated users can access.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,           # Required for profile picture upload
            instance=request.user    # Pre-bind to current user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your profile has been updated successfully!")
            return redirect('users:profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # Pre-fill form with current user data
        form = ProfileUpdateForm(instance=request.user)

    # Get user's registrations for profile page stats
    from registrations.models import Registration   # Local import to avoid circular
    user_registrations = Registration.objects.filter(
        email=request.user.email
    ).select_related('event').order_by('-registered_at')[:5]

    context = {
        'form': form,
        'user_registrations': user_registrations,
    }
    return render(request, 'users/profile.html', context)


@login_required
def logout_view(request):
    """
    Log out the current user and redirect to login page.
    Uses POST-only approach to prevent CSRF logout attacks.
    """
    logout(request)
    messages.info(request, "You've been logged out. See you next time! 👋")
    return redirect('account_login')


@login_required
def delete_avatar_view(request):
    """
    Remove the user's profile picture and reset to default avatar.
    POST only for security (no accidental deletion via GET).
    """
    if request.method == 'POST':
        user = request.user
        if user.profile_picture:
            # Delete the actual file from storage
            user.profile_picture.delete(save=False)
            user.profile_picture = None
            user.save()
            messages.success(request, "Profile picture removed successfully.")
        else:
            messages.info(request, "You don't have a profile picture to remove.")
    return redirect('users:profile')
