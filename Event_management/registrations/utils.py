# ============================================================
# File: registrations/utils.py
# Django Event Management System — QR Code + PDF + Email Utils
# Skills Applied: django-backend + copywriting
# ============================================================

import os
import io
import uuid
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# ── QR Code Generator ────────────────────────────────────────

def generate_qr_code(registration):
    """
    Generate a QR code image for the given registration.
    Encodes: ticket_number|event_id|email for verification.
    Saves to media/qr_codes/<ticket_number>.png.
    Returns the saved ImageField file.
    """
    # Build QR data string (ticket_number for uniqueness)
    ticket = registration.ticket
    qr_data = (
        f"EVENTHUB|"
        f"TICKET:{str(ticket.ticket_number)}|"
        f"EVENT:{registration.event.id}|"
        f"EMAIL:{registration.email}"
    )

    # Create QR code with styling
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create image with custom colors
    img = qr.make_image(
        fill_color='#1a1a2e',    # Dark navy
        back_color='white'
    )

    # Save to bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Save to registration's qr_code field
    filename = f"qr_{str(ticket.ticket_number)[:8]}.png"
    registration.qr_code.save(filename, ContentFile(buffer.read()), save=True)

    return registration.qr_code


def generate_pdf_ticket(registration):
    """
    Generate a PDF ticket for the given registration using ReportLab.
    Includes: event details, attendee name, QR code, ticket number.
    Saves to media/tickets/<ticket_number>.pdf.
    Returns the saved FileField.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    ticket = registration.ticket
    event = registration.event

    # Build PDF in memory
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    # Styles
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'title',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        'subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    style_heading = ParagraphStyle(
        'heading',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#8b949e'),
        fontName='Helvetica',
    )
    style_value = ParagraphStyle(
        'value',
        parent=styles['Normal'],
        fontSize=13,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
    )
    style_ticket_num = ParagraphStyle(
        'ticket_num',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#6366f1'),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )

    story = []

    # ── Header ─────────────────────────────────────────────
    story.append(Paragraph("🎫 EventHub", style_title))
    story.append(Paragraph("Your Official Ticket", style_subtitle))
    story.append(Spacer(1, 8*mm))

    # ── Ticket Number ───────────────────────────────────────
    story.append(Paragraph(
        f"Ticket No: #{ticket.ticket_number_short}",
        style_ticket_num
    ))
    story.append(Spacer(1, 6*mm))

    # ── Event Details Table ─────────────────────────────────
    table_data = [
        [Paragraph("Event", style_heading),    Paragraph(event.title, style_value)],
        [Paragraph("Date", style_heading),     Paragraph(event.date.strftime('%A, %B %d, %Y'), style_value)],
        [Paragraph("Time", style_heading),     Paragraph(event.date.strftime('%I:%M %p'), style_value)],
        [Paragraph("Venue", style_heading),    Paragraph(event.location, style_value)],
        [Paragraph("Attendee", style_heading), Paragraph(registration.name, style_value)],
        [Paragraph("Email", style_heading),    Paragraph(registration.email, style_value)],
        [Paragraph("Price", style_heading),    Paragraph(event.price_display, style_value)],
        [Paragraph("Status", style_heading),   Paragraph("✅ CONFIRMED", style_value)],
    ]

    table = Table(table_data, colWidths=[40*mm, 130*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(table)
    story.append(Spacer(1, 8*mm))

    # ── QR Code ─────────────────────────────────────────────
    if registration.qr_code:
        qr_path = registration.qr_code.path
        if os.path.exists(qr_path):
            qr_img = RLImage(qr_path, width=50*mm, height=50*mm)
            story.append(qr_img)
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph(
                "Scan this QR code at the venue for entry",
                ParagraphStyle('qr_note', parent=styles['Normal'],
                               fontSize=9, textColor=colors.HexColor('#94a3b8'),
                               alignment=TA_CENTER)
            ))

    # ── Footer ──────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "This ticket is your proof of registration. Please bring it to the event (printed or digital).",
        ParagraphStyle('footer', parent=styles['Normal'],
                       fontSize=9, textColor=colors.HexColor('#94a3b8'),
                       alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    # Save to ticket's pdf_file field
    filename = f"ticket_{ticket.ticket_number_short}.pdf"
    ticket.pdf_file.save(filename, ContentFile(buffer.read()), save=True)

    return ticket.pdf_file


# ── Email Sender ─────────────────────────────────────────────

def send_confirmation_email(registration):
    """
    Send HTML confirmation email with ticket details.
    copywriting: warm, celebratory tone with clear CTAs.
    Attaches the PDF ticket if generated.
    """
    ticket = getattr(registration, 'ticket', None)
    subject = f"🎉 You're in! Your ticket for {registration.event.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [registration.email]

    # Render HTML email from template
    html_content = render_to_string('emails/ticket_confirmation.html', {
        'registration': registration,
        'event': registration.event,
        'ticket': ticket,
        'site_url': settings.SITE_URL,
        'site_name': settings.SITE_NAME,
    })
    text_content = strip_tags(html_content)

    # Build email
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, 'text/html')

    # Attach PDF ticket if it exists
    if ticket and ticket.pdf_file:
        try:
            with open(ticket.pdf_file.path, 'rb') as f:
                msg.attach(
                    f"EventHub_Ticket_{ticket.ticket_number_short}.pdf",
                    f.read(),
                    'application/pdf'
                )
        except Exception:
            pass  # PDF unavailable — still send email without it

    # Send and mark as sent
    try:
        msg.send()
        registration.confirmation_sent = True
        registration.save(update_fields=['confirmation_sent'])
    except Exception as e:
        # Log but don't crash — email failure shouldn't break registration
        print(f"[EMAIL ERROR] Failed to send confirmation to {registration.email}: {e}")
