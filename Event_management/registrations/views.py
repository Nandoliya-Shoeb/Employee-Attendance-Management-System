# ============================================================
# File: registrations/views.py
# Django Event Management System — Registration Views
# Skills Applied: django-backend + owasp-security + copywriting
# Rules: FBVs only. @login_required on protected views.
#        Every function commented. ORM only. No raw SQL.
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import FileResponse, Http404
from django.db import transaction

from events.models import Event
from .models import Registration, Ticket
from .forms import RegistrationForm
from .utils import generate_qr_code, generate_pdf_ticket, send_confirmation_email

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Configure Razorpay Client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# ── PUBLIC REGISTRATION FLOW ──────────────────────────────────

@login_required
@require_http_methods(["GET", "POST"])
def register_for_event(request, event_id):
    """
    Handle event registration flow.
    GET  → Show registration form (pre-filled if logged in).
    POST → Validate, reserve seat, generate QR+PDF, send email.
    Security: @login_required prevents anonymous registrations.
    Business rules: duplicate check + seat check in form.clean().
    Uses atomic transaction to prevent partial saves.
    """
    event = get_object_or_404(Event, pk=event_id, status=Event.STATUS_PUBLISHED)

    # Redirect if already registered
    existing = Registration.objects.filter(
        event=event,
        email=request.user.email,
        status__in=[Registration.STATUS_CONFIRMED, Registration.STATUS_PENDING]
    ).first()

    if existing:
        messages.info(request, "You're already registered for this event!")
        return redirect('registrations:registration_detail', pk=existing.pk)

    # Redirect if event is full or past
    if event.is_full:
        messages.error(request, "Sorry, this event is sold out!")
        return redirect('events:event_detail', slug=event.slug)

    if event.is_past:
        messages.error(request, "Registration has closed for this event.")
        return redirect('events:event_detail', slug=event.slug)

    if request.method == 'POST':
        form = RegistrationForm(
            request.POST,
            event=event,
            user=request.user
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    # ── Step 1: Create Registration ───────────────
                    registration = form.save(commit=False)
                    registration.event = event
                    registration.user = request.user

                    # Free events auto-confirm immediately
                    if event.is_free:
                        registration.status = Registration.STATUS_CONFIRMED
                    else:
                        registration.status = Registration.STATUS_PENDING  # Awaits payment

                    registration.save()

                    # ── Step 2: Create Ticket ────────────────────
                    ticket = Ticket.objects.create(registration=registration)

                    # ── Step 3: Generate QR Code ─────────────────
                    generate_qr_code(registration)

                    # ── Step 4: Generate PDF Ticket ───────────────
                    generate_pdf_ticket(registration)

                    # ── Step 5: Dispatch Task ─────────────────────
                    # If free, auto-confirm and send email via task
                    if event.is_free:
                        from .tasks import send_confirmation_email_task
                        send_confirmation_email_task.delay(registration.pk)

                    # ── Step 6: Redirect to success page ──────────
                    if event.is_free:
                        messages.success(
                            request,
                            f"🎉 You're registered! Check your email for your ticket."
                        )
                        return redirect('registrations:success', pk=registration.pk)
                    else:
                        # Paid events → redirect to payment
                        return redirect('registrations:payment', pk=registration.pk)

            except Exception as e:
                messages.error(
                    request,
                    f"Something went wrong during registration. Please try again. ({str(e)})"
                )
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegistrationForm(event=event, user=request.user)

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'registrations/register_form.html', context)


def registration_success(request, pk):
    """
    Show success page after registration.
    Displays ticket details and confetti animation (i-motion skill).
    Public: anyone with the pk can view (for sharing/screenshot).
    """
    registration = get_object_or_404(Registration, pk=pk)

    # Verify it belongs to the logged-in user (or allow staff)
    if request.user.is_authenticated:
        if (registration.user != request.user and
                not request.user.is_staff and
                registration.email != request.user.email):
            messages.error(request, "You don't have permission to view this ticket.")
            return redirect('events:event_list')

    context = {
        'registration': registration,
        'ticket': getattr(registration, 'ticket', None),
    }
    return render(request, 'registrations/registration_success.html', context)


@login_required
def my_registrations(request):
    """
    Show all registrations for the logged-in user.
    Sorted by most recent first. Includes links to tickets.
    """
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('event', 'event__category', 'ticket').order_by('-registered_at')

    # Split by status for tabs
    confirmed = registrations.filter(status=Registration.STATUS_CONFIRMED)
    pending   = registrations.filter(status=Registration.STATUS_PENDING)
    cancelled = registrations.filter(status=Registration.STATUS_CANCELLED)

    context = {
        'registrations': registrations,
        'confirmed': confirmed,
        'pending': pending,
        'cancelled': cancelled,
        'total': registrations.count(),
    }
    return render(request, 'registrations/my_registrations.html', context)


# Alias for the stub URL 'registration_list'
registration_list = my_registrations


@login_required
def registration_detail(request, pk):
    """
    Show detail page for a single registration / ticket.
    Allows download of PDF ticket.
    """
    registration = get_object_or_404(
        Registration,
        pk=pk,
        user=request.user
    )
    ticket = getattr(registration, 'ticket', None)

    context = {
        'registration': registration,
        'ticket': ticket,
    }
    return render(request, 'registrations/registration_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def cancel_registration(request, pk):
    """
    Cancel a confirmed registration.
    GET  → Show confirmation page (ui-ux-pro-max: confirm before destructive action).
    POST → Cancel and redirect to my tickets.
    owasp-security: verify ownership before allowing cancellation.
    """
    registration = get_object_or_404(
        Registration,
        pk=pk,
        user=request.user
    )

    # Security: only the owner can cancel
    if registration.user != request.user:
        messages.error(request, "You don't have permission to cancel this registration.")
        return redirect('registrations:my_registrations')

    # Check if cancellation is allowed
    if not registration.can_cancel:
        if registration.is_cancelled:
            messages.warning(request, "This registration is already cancelled.")
        else:
            messages.error(request, "This event has already started — cancellation is not possible.")
        return redirect('registrations:my_registrations')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        registration.cancel(reason=reason)

        messages.success(
            request,
            f"Your registration for '{registration.event.title}' has been cancelled. "
            "We hope to see you at a future event!"
        )
        return redirect('registrations:my_registrations')

    return render(request, 'registrations/cancel_confirm.html', {
        'registration': registration,
    })


@login_required
def download_ticket(request, pk):
    """
    Stream the PDF ticket file to the browser for download.
    Security: verify the registration belongs to the logged-in user.
    """
    registration = get_object_or_404(
        Registration,
        pk=pk,
        user=request.user,
        status=Registration.STATUS_CONFIRMED
    )

    ticket = getattr(registration, 'ticket', None)

    if not ticket or not ticket.pdf_file:
        messages.error(request, "Ticket PDF not found. Please contact support.")
        return redirect('registrations:registration_detail', pk=pk)

    try:
        response = FileResponse(
            open(ticket.pdf_file.path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="EventHub_Ticket_{ticket.ticket_number_short}.pdf"'
        )
        return response
    except FileNotFoundError:
        raise Http404("Ticket PDF file not found.")


@login_required
def payment_page(request, pk):
    """
    Show payment page for pending registration.
    Step 7 — Razorpay integration.
    """
    registration = get_object_or_404(
        Registration,
        pk=pk,
        user=request.user,
        status=Registration.STATUS_PENDING
    )
    event = registration.event
    amount_in_paise = int(event.price * 100)

    # 1. Create Razorpay Order
    razorpay_order = razorpay_client.order.create({
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1',
        'notes': {
            'registration_id': registration.id,
            'event_id': event.id
        }
    })

    context = {
        'registration': registration,
        'event': event,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,
        'currency': 'INR',
    }
    return render(request, 'registrations/payment.html', context)


@csrf_exempt
def payment_callback(request, pk):
    """
    Callback URL where Razorpay posts the payment payload after checkout.
    Verifies signature and confirms the registration.
    """
    registration = get_object_or_404(Registration, pk=pk)

    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        # Construct dictionary for verification
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # 2. Verify Payment Signature
            razorpay_client.utility.verify_payment_signature(params_dict)

            # If here, payment matches exactly. Mark confirmed!
            registration.status = Registration.STATUS_CONFIRMED
            registration.save()

            # 3. Offload sending the PDF confirmation email to Celery
            from .tasks import send_confirmation_email_task
            send_confirmation_email_task.delay(registration.pk)

            messages.success(request, "🎉 Payment successful! Your ticket is confirmed.")
            return redirect('registrations:success', pk=registration.pk)

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. If money was deducted, it will be refunded.")
            return redirect('registrations:payment', pk=registration.pk)

    return redirect('registrations:my_registrations')
