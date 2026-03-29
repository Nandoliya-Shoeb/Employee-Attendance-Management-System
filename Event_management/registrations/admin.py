# ============================================================
# File: registrations/admin.py
# Django Event Management System — Registrations Admin
# ============================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Registration, Ticket


class TicketInline(admin.StackedInline):
    """Show ticket details inline within registration admin."""
    model = Ticket
    readonly_fields = ('ticket_number', 'pdf_file', 'issued_at')
    extra = 0
    can_delete = False


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Admin configuration for Registration model."""

    list_display = (
        'name', 'email', 'event', 'status_badge',
        'confirmation_sent', 'registered_at'
    )
    list_filter = ('status', 'confirmation_sent', 'event', 'registered_at')
    search_fields = ('name', 'email', 'phone', 'event__title')
    ordering = ('-registered_at',)
    readonly_fields = ('registered_at', 'updated_at', 'cancelled_at')
    inlines = [TicketInline]

    fieldsets = (
        ('Registrant', {
            'fields': ('name', 'email', 'phone', 'user')
        }),
        ('Event', {
            'fields': ('event',)
        }),
        ('Status', {
            'fields': ('status', 'qr_code', 'confirmation_sent')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancel_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('registered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Colored status badge in list view."""
        colors_map = {
            'confirmed': ('#22c55e', '✅'),
            'pending':   ('#f59e0b', '⏳'),
            'cancelled': ('#ef4444', '❌'),
        }
        color, icon = colors_map.get(obj.status, ('#8b949e', '•'))
        return format_html(
            '<span style="color:{}; font-weight:600;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin configuration for Ticket model."""
    list_display = ('ticket_number_short', 'registration', 'issued_at', 'has_pdf')
    search_fields = ('ticket_number', 'registration__name', 'registration__email')
    readonly_fields = ('ticket_number', 'issued_at')

    def ticket_number_short(self, obj):
        """Show short ticket number."""
        return f"#{obj.ticket_number_short}"
    ticket_number_short.short_description = 'Ticket #'

    def has_pdf(self, obj):
        """Show PDF availability."""
        if obj.pdf_file:
            return format_html('<span style="color:#22c55e;">✅ Available</span>')
        return format_html('<span style="color:#ef4444;">❌ Missing</span>')
    has_pdf.short_description = 'PDF'
