# ============================================================
# File: events/views.py
# Django Event Management System — Events App Views (Stub)
# Full views built in Step 3
# ============================================================

from django.shortcuts import render


def event_list(request):
    """Display list of all public events. (Full view built in Step 3)"""
    return render(request, 'events/event_list.html')
