# ============================================================
# File: events/forms.py
# Django Event Management System — Event Forms (Admin)
# Skills Applied: django-backend + frontend-design
# ============================================================

from django import forms
from django.utils import timezone
from .models import Event, Category


class EventForm(forms.ModelForm):
    """
    Form for creating and editing events (admin only).
    Used in admin CRUD views. All fields validated for correctness.
    """

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter event title',
        })
    )

    short_description = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Short teaser (shown on event cards)',
        })
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Full event description...',
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='— Select Category —',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    location = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Venue name and address',
        })
    )

    location_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://maps.google.com/...',
        })
    )

    is_online = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    online_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://zoom.us/j/...',
        })
    )

    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    max_capacity = forms.IntegerField(
        min_value=1,
        initial=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100',
        })
    )

    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00 (free)',
            'min': '0',
        })
    )

    status = forms.ChoiceField(
        choices=Event.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Event
        fields = [
            'title', 'short_description', 'description',
            'category', 'date', 'end_date',
            'location', 'location_url', 'is_online', 'online_link',
            'cover_image', 'max_capacity', 'price',
            'status', 'is_featured',
        ]

    def clean(self):
        """Validate form-level logic: date ordering, online link."""
        cleaned = super().clean()
        date = cleaned.get('date')
        end_date = cleaned.get('end_date')

        # End date must be after start date
        if date and end_date and end_date <= date:
            raise forms.ValidationError(
                "End date must be after the start date."
            )

        # Online events must have a meeting link
        is_online = cleaned.get('is_online')
        online_link = cleaned.get('online_link')
        if is_online and not online_link:
            raise forms.ValidationError(
                "Please provide a meeting link for the online event."
            )

        return cleaned


class EventSearchForm(forms.Form):
    """
    Search and filter form for the public event listing page.
    No authentication required — used by all visitors.
    """

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...',
            'id': 'searchInput',
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'categoryFilter',
        })
    )

    price_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Any Price'),
            ('free', 'Free'),
            ('paid', 'Paid'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'priceFilter',
        })
    )

    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('date', 'Upcoming First'),
            ('-date', 'Latest First'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('title', 'A to Z'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'sortFilter',
        })
    )
