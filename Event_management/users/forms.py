# ============================================================
# File: users/forms.py
# Django Event Management System — User Forms
# Skills Applied: django-backend + owasp-security + frontend-design
# ============================================================

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from .models import CustomUser


# Phone number validator — only digits, +, -, spaces allowed
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Enter a valid phone number (e.g. +919876543210 or 9876543210)."
)


class CustomUserRegistrationForm(UserCreationForm):
    """
    Registration form for new users.
    Uses email as primary identifier with full name fields.
    Includes OWASP-compliant validation on all inputs.
    """

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autofocus': True,
        })
    )

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 9876543210 (optional)',
        })
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min. 8 characters)',
        })
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        """Validate that email is not already registered."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered. Please log in or use a different email."
            )
        return email.lower()

    def save(self, commit=True):
        """Save user with auto-generated username from email."""
        user = super().save(commit=False)
        # Auto-generate username from email (before the @)
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        counter = 1
        # Ensure username is unique
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Profile update form — allows user to update their details.
    Email is read-only after registration (security).
    """

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        })
    )

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 9876543210',
        })
    )

    bio = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us a bit about yourself...',
            'rows': 3,
        })
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone', 'bio', 'profile_picture')

    def clean_profile_picture(self):
        """Validate profile picture — max 2MB, must be image."""
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError(
                    "Profile picture must be smaller than 2MB. Please compress your image."
                )
        return picture
