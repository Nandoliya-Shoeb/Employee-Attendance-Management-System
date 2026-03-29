# ============================================================
# File: users/views.py
# Django Event Management System — Users App Views (Stub)
# Full views built in Step 2
# ============================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile_view(request):
    """Display and update user profile. (Full view built in Step 2)"""
    return render(request, 'users/profile.html')
