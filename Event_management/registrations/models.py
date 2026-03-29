# ============================================================
# File: registrations/models.py
# Django Event Management System — Registration & Ticket Models
# Skills Applied: django-backend + database-design
# Rules: snake_case, created_at+updated_at, FK on_delete, __str__
# ============================================================

import uuid
from django.db import models
from django.utils import timezone


class Registration(models.Model):
    """
    Core Registration model — links a person to an event.
    Each registration gets a unique QR code for ticket verification.
    Status tracks the lifecycle: pending → confirmed → cancelled.
    """

    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    # Link to the event being registered for
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='registrations',
        help_text='Event this registration is for.'
    )

    # Registrant details (stored separately for flexibility)
    name = models.CharField(
        max_length=150,
        help_text='Full name of the attendee.'
    )
    email = models.EmailField(
        help_text='Email address — used for ticket delivery.'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Phone number (optional).'
    )

    # Link to user account if they were logged in during registration
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations',
        help_text='Linked user account (if logged in).'
    )

    # QR Code image stored in media/qr_codes/
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True,
        help_text='Auto-generated QR code image for ticket verification.'
    )

    # Booking status
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text='Pending until payment confirmed (or free events auto-confirm).'
    )

    # Cancellation tracking
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when registration was cancelled.'
    )
    cancel_reason = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text='Reason provided for cancellation.'
    )

    # Email notification tracking
    confirmation_sent = models.BooleanField(
        default=False,
        help_text='True when confirmation email has been sent.'
    )

    # Timestamps — database-design requirement
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        ordering = ['-registered_at']
        # Prevent same email from registering for same event twice
        unique_together = [['event', 'email']]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        """Return registrant name and event title."""
        return f"{self.name} → {self.event.title}"

    def cancel(self, reason=''):
        """
        Cancel this registration and record timestamp + reason.
        Called from cancel_registration view.
        """
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = timezone.now()
        self.cancel_reason = reason
        self.save(update_fields=['status', 'cancelled_at', 'cancel_reason', 'updated_at'])

    @property
    def is_confirmed(self):
        """Check if registration is confirmed."""
        return self.status == self.STATUS_CONFIRMED

    @property
    def is_cancelled(self):
        """Check if registration has been cancelled."""
        return self.status == self.STATUS_CANCELLED

    @property
    def can_cancel(self):
        """Check if registration can still be cancelled (event not started)."""
        return (
            self.status == self.STATUS_CONFIRMED and
            self.event.date > timezone.now()
        )


class Ticket(models.Model):
    """
    Ticket model — issued after successful registration.
    ticket_number is a UUID for secure, unique identification.
    Stores the generated PDF file path.
    """

    # One ticket per registration
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='ticket',
        help_text='The registration this ticket belongs to.'
    )

    # UUID ticket number — harder to guess than sequential IDs
    ticket_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Unique ticket identifier (UUID).'
    )

    # PDF ticket file stored in media/tickets/
    pdf_file = models.FileField(
        upload_to='tickets/',
        null=True,
        blank=True,
        help_text='Generated PDF ticket file.'
    )

    # Timestamps — database-design requirement
    issued_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-issued_at']

    def __str__(self):
        """Return ticket number and attendee name."""
        return f"Ticket #{str(self.ticket_number)[:8].upper()} — {self.registration.name}"

    @property
    def ticket_number_short(self):
        """Return first 8 chars of UUID for display."""
        return str(self.ticket_number)[:8].upper()
