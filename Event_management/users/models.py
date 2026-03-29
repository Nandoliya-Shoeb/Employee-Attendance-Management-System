# ============================================================
# File: users/models.py
# Django Event Management System — Custom User Model (Stub)
# Full implementation in Step 2
# Skills Applied: django-backend + database-design + owasp-security
# ============================================================

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Defined here in Step 1 so AUTH_USER_MODEL can reference it.
    Full fields (role, avatar, phone) added in Step 2.
    """
    # Step 2 will add: role, profile_picture, phone, bio
    # Using AbstractUser gives us: username, email, password,
    # first_name, last_name, is_staff, is_active, date_joined

    def __str__(self):
        """Return email as string representation of user."""
        return self.email or self.username
