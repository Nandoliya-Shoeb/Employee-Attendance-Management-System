# ============================================================
# File: registrations/urls.py
# Django Event Management System — Registrations URL Config
# ============================================================

from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    # My Tickets page
    path('', views.my_registrations, name='registration_list'),
    path('my-tickets/', views.my_registrations, name='my_registrations'),

    # Register for an event
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),

    # Registration success (with confetti)
    path('<int:pk>/success/', views.registration_success, name='success'),

    # Registration detail / ticket view
    path('<int:pk>/', views.registration_detail, name='registration_detail'),

    # Cancel registration
    path('<int:pk>/cancel/', views.cancel_registration, name='cancel'),

    # Download PDF ticket
    path('<int:pk>/download/', views.download_ticket, name='download_ticket'),

    # Payment page & callback (Step 7 — Razorpay)
    path('<int:pk>/payment/', views.payment_page, name='payment'),
    path('<int:pk>/payment/callback/', views.payment_callback, name='payment_callback'),
]
