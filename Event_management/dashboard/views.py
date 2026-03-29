# ============================================================
# File: dashboard/views.py
# Django Event Management System — Dashboard Views (Stub)
# Full views built in Step 5
# ============================================================

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def dashboard_home(request):
    """Admin dashboard home page. (Full view built in Step 5)"""
    return render(request, 'dashboard/home.html')
