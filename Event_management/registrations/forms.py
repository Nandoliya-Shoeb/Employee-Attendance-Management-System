# ============================================================
# File: registrations/forms.py
# Django Event Management System — Registration Form
# Skills Applied: django-backend + owasp-security + copywriting
# ============================================================

from django import forms
from django.core.validators import RegexValidator
from .models import Registration


phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Enter a valid phone number (e.g. +919876543210)."
)


class RegistrationForm(forms.ModelForm):
    """
    Public registration form — collects attendee details.
    Validates: no duplicate registrations, event not full,
    event is still upcoming, input sanitization (owasp-security).
    copywriting: friendly placeholder text and error messages.
    """

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Your full name',
            'autofocus': True,
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your@email.com',
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '+91 9876543210 (optional)',
        })
    )

    class Meta:
        model = Registration
        fields = ['name', 'email', 'phone']

    def __init__(self, *args, event=None, user=None, **kwargs):
        """
        Accept event and user to perform context-aware validation.
        Pre-fill form if user is logged in.
        """
        super().__init__(*args, **kwargs)
        self.event = event
        self.user = user

        # Pre-fill fields if user is authenticated
        if user and user.is_authenticated:
            self.fields['email'].widget.attrs['readonly'] = True
            self.initial['name'] = user.get_full_name() or user.username
            self.initial['email'] = user.email
            self.initial['phone'] = user.phone or ''

    def clean_email(self):
        """
        Validate email: check for duplicate registration for this event.
        Friendly error: tell user exactly what to do next.
        """
        email = self.cleaned_data.get('email', '').lower().strip()

        if self.event:
            # Duplicate check — owasp-security: prevent double booking
            already_registered = Registration.objects.filter(
                event=self.event,
                email=email,
                status__in=[Registration.STATUS_CONFIRMED, Registration.STATUS_PENDING]
            ).exists()

            if already_registered:
                raise forms.ValidationError(
                    "You're already registered for this event! "
                    "Check your email for your ticket, or visit 'My Tickets'."
                )

        return email

    def clean(self):
        """
        Form-level validation: check seats availability and event status.
        These are business rules that apply across all fields.
        """
        cleaned = super().clean()

        if self.event:
            # Check event is still published
            if self.event.status != 'published':
                raise forms.ValidationError(
                    "This event is no longer accepting registrations."
                )

            # Check event hasn't passed
            from django.utils import timezone
            if self.event.date <= timezone.now():
                raise forms.ValidationError(
                    "Sorry, registration for this event has closed. "
                    "The event has already started or ended."
                )

            # Check seats available
            if self.event.is_full:
                raise forms.ValidationError(
                    "Sorry, this event is sold out! "
                    "All seats have been filled. Check back for cancellations."
                )

        return cleaned
