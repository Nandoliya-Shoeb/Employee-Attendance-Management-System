# ============================================================
# File: users/admin.py
# Django Event Management System — Custom User Admin
# Skills Applied: django-backend
# ============================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    Extends default UserAdmin to include our custom fields.
    """

    # Columns shown in the user list
    list_display = (
        'email', 'first_name', 'last_name',
        'role', 'is_staff', 'is_active', 'created_at'
    )

    # Filters in the right sidebar
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')

    # Fields used for searching
    search_fields = ('email', 'first_name', 'last_name', 'phone')

    # Field used for ordering
    ordering = ('-created_at',)

    # Add our custom fields to the edit form sections
    fieldsets = UserAdmin.fieldsets + (
        ('EventHub Profile', {
            'fields': ('role', 'profile_picture', 'phone', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Read-only timestamp fields
    readonly_fields = ('created_at', 'updated_at')

    # Fields shown on the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'role', 'phone', 'password1', 'password2'
            ),
        }),
    )
