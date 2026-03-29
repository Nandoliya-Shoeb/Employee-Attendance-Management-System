# ============================================================
# File: events/admin.py
# Django Event Management System — Events Admin Configuration
# ============================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Event, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for event categories."""
    list_display = ('name', 'slug', 'icon', 'color')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin configuration for Event model.
    Includes list filters, search, inline registration count.
    """

    # Columns in list view
    list_display = (
        'title', 'category', 'date', 'location',
        'status_badge', 'price_display', 'seats_info',
        'is_featured', 'created_at'
    )

    # Sidebar filters
    list_filter = ('status', 'category', 'is_featured', 'is_online', 'date')

    # Search fields
    search_fields = ('title', 'description', 'location')

    # Click-to-edit columns
    list_editable = ('is_featured',)

    # Auto-populate slug from title
    prepopulated_fields = {'slug': ('title',)}

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at', 'seats_remaining_display')

    # Date hierarchy for browsing
    date_hierarchy = 'date'

    # Field grouping in edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'category')
        }),
        ('Date & Location', {
            'fields': ('date', 'end_date', 'location', 'location_url', 'is_online', 'online_link')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Capacity & Pricing', {
            'fields': ('max_capacity', 'price', 'seats_remaining_display')
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'organizer')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Show colored status badge in list view."""
        colors = {
            'draft': '#8b949e',
            'published': '#22c55e',
            'cancelled': '#ef4444',
            'completed': '#6366f1',
        }
        color = colors.get(obj.status, '#8b949e')
        return format_html(
            '<span style="background:{}20; color:{}; padding:2px 8px; '
            'border-radius:12px; font-size:0.75rem; font-weight:600;">{}</span>',
            color, color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def price_display(self, obj):
        """Show price or 'Free' label."""
        return obj.price_display
    price_display.short_description = 'Price'

    def seats_info(self, obj):
        """Show seats taken / total in list view."""
        return f"{obj.seats_taken} / {obj.max_capacity}"
    seats_info.short_description = 'Seats'

    def seats_remaining_display(self, obj):
        """Read-only seats remaining field in detail view."""
        return f"{obj.seats_remaining} seats remaining out of {obj.max_capacity}"
    seats_remaining_display.short_description = 'Seats Remaining'
