# ============================================================
# File: users/models.py
# Django Event Management System — Custom User + Profile Models
# Skills Applied: django-backend + database-design + owasp-security
# ============================================================

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses email as the primary login field (no username needed).
    Role field determines admin vs regular user access.
    Timestamps follow database-design skill: created_at + updated_at.
    """

    # Role choices — determines access level
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    ]

    # Override email to make it required and unique
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text='Required. Enter a valid email address.'
    )

    # Role field — controls admin dashboard access
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        help_text='Admin can manage events. User can register for events.'
    )

    # Profile picture — stored in media/avatars/
    profile_picture = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='Upload a profile picture (JPG/PNG, max 2MB).'
    )

    # Phone number — optional, used for ticket contact
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Phone number with country code (e.g. +91 9876543210).'
    )

    # Short bio — optional, shown on profile page
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=300,
        help_text='Tell us a bit about yourself (max 300 characters).'
    )

    # Timestamps — database-design skill requirement
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the login field instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        """Return full name or email as string representation."""
        return self.get_full_name() or self.email

    def is_admin_user(self):
        """Check if user has admin role — used in templates and views."""
        return self.role == self.ROLE_ADMIN or self.is_staff

    def get_avatar_url(self):
        """Return profile picture URL or default avatar path."""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default_avatar.png'
