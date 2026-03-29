# ============================================================
# File: utils/pdf_generator.py
# Django Event Management System — PDF Generator Proxy
# ============================================================
from registrations.utils import generate_pdf_ticket

def generate_pdf(registration):
    """Facade for pdf generation"""
    return generate_pdf_ticket(registration)
