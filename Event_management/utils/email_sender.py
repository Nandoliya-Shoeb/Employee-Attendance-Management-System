# ============================================================
# File: utils/email_sender.py
# Django Event Management System — Email Sender Proxy
# ============================================================
from registrations.utils import send_confirmation_email

def send_email(registration):
    """Facade for email generation"""
    return send_confirmation_email(registration)
