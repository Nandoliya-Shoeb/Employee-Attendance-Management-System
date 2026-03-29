# ============================================================
# File: utils/qr_generator.py
# Django Event Management System — QR Generator Proxy
# ============================================================
from registrations.utils import generate_qr_code

def generate_qr(registration):
    """Facade for qr generation"""
    return generate_qr_code(registration)
