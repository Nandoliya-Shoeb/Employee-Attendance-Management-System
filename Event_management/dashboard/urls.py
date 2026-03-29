# ============================================================
# File: dashboard/urls.py
# Django Event Management System — Dashboard URL Config
# ============================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home
    path('', views.dashboard_home, name='home'),

    # JSON API endpoint for Chart.js
    path('api/chart-data/', views.chart_data_api, name='chart_data'),

    # CSV Export endpoint
    path('export/registrations/', views.export_registrations_csv, name='export_registrations'),
]
