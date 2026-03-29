# ============================================================
# File: registrations/views.py
# Django Event Management System — Registrations Views (Stub)
# Full views built in Step 4
# ============================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def registration_list(request):
    """Display user's registrations. (Full view built in Step 4)"""
    return render(request, 'registrations/my_registrations.html')
