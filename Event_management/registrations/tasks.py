# ============================================================
# File: registrations/tasks.py
# Django Event Management System — Celery Tasks
# Skills Applied: message-queues + backend-scale
# ============================================================

from celery import shared_task
from django.core.mail import mail_admins
from .models import Registration
from .utils import send_confirmation_email

@shared_task(bind=True, max_retries=3)
def send_confirmation_email_task(self, registration_id):
    """
    Celery task to send a registration confirmation email asynchronously.
    Prevents the UI from hanging while ReportLab generates PDFs or SMTP sends emails.
    Retries up to 3 times on failure.
    """
    try:
        # Fetch the registration (must be confirmed)
        registration = Registration.objects.get(pk=registration_id, status=Registration.STATUS_CONFIRMED)
        
        # Call the existing sync utility function
        send_confirmation_email(registration)
        
        return f"Successfully sent confirmation to {registration.email}"

    except Registration.DoesNotExist:
        return f"Registration {registration_id} not found."
    except Exception as exc:
        # Retry with exponential backoff (e.g. 60s, 120s, 240s)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_pending_registrations():
    """
    Periodic Celery Task (e.g. run every 1 hour via Celery Beat).
    Finds PENDING registrations older than 2 hours and cancels them,
    freeing up seats for other attendees.
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_time = timezone.now() - timedelta(hours=2)
    
    abandoned_regs = Registration.objects.filter(
        status=Registration.STATUS_PENDING,
        registered_at__lt=cutoff_time
    )

    count = abandoned_regs.count()
    if count > 0:
        # Iterate over them so the cancel logic (timestamping) applies
        for reg in abandoned_regs:
            reg.cancel(reason="System Auto-Cancel: Payment window expired (2 hours).")
            
        mail_admins(
            subject='EventHub Admin: Abandoned Registrations Cancelled',
            message=f'The system auto-cancelled {count} pending registrations that didn\'t complete payment in time.'
        )
        
    return f"Cleaned up {count} abandoned pending registrations."
