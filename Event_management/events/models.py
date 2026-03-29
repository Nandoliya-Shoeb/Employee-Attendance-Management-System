# ============================================================
# File: events/models.py
# Django Event Management System — Event Model
# Skills Applied: django-backend + database-design
# Rules: snake_case fields, created_at+updated_at on every model,
#        FK with on_delete, __str__ on every model, 3NF minimum.
# ============================================================

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Event category model (Technology, Music, Sports, etc.).
    Normalized separately per 3NF — database-design skill.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(
        max_length=50,
        default='bi-calendar-event',
        help_text='Bootstrap icon class e.g. bi-laptop'
    )
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text='Hex color for category badge'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        """Return category name as string."""
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name on save."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """
    Core Event model — stores all event information.
    Status controls visibility (draft/published/cancelled/completed).
    All fields follow database-design skill: snake_case, timestamps, FK on_delete.
    """

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_DRAFT,     'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    # Core Fields
    title = models.CharField(
        max_length=200,
        help_text='Event title (max 200 characters)'
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text='URL-friendly version of title (auto-generated)'
    )
    description = models.TextField(
        help_text='Full event description. Supports HTML.'
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text='Short teaser shown on event cards (max 300 chars)'
    )

    # Category — FK with on_delete per database-design skill
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        help_text='Event category'
    )

    # Date & Location
    date = models.DateTimeField(help_text='Event start date and time')
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Event end date and time (optional)'
    )
    location = models.CharField(
        max_length=300,
        help_text='Venue name and address'
    )
    location_url = models.URLField(
        blank=True,
        null=True,
        help_text='Google Maps link (optional)'
    )
    is_online = models.BooleanField(
        default=False,
        help_text='Is this an online event?'
    )
    online_link = models.URLField(
        blank=True,
        null=True,
        help_text='Online meeting link (Zoom, Meet, etc.)'
    )

    # Media
    cover_image = models.ImageField(
        upload_to='events/',
        null=True,
        blank=True,
        help_text='Event cover image (recommended: 1200x600px)'
    )

    # Capacity & Pricing
    max_capacity = models.PositiveIntegerField(
        default=100,
        help_text='Maximum number of attendees'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Ticket price (0.00 = free event)'
    )

    # Status
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text='Draft = not visible. Published = visible to public.'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Show in featured/hero section on homepage'
    )

    # Organizer (FK to user who created it)
    organizer = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
        help_text='Event organizer/admin'
    )

    # Timestamps — database-design skill requirement
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['date']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        """Return event title and date as string."""
        return f"{self.title} ({self.date.strftime('%d %b %Y')})"

    def save(self, *args, **kwargs):
        """Auto-generate unique slug from title on save."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Auto-generate short_description from description if not set
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + '...'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the canonical URL for this event."""
        return reverse('events:event_detail', kwargs={'slug': self.slug})

    # ── Computed Properties ─────────────────────────────────

    @property
    def is_free(self):
        """Check if event is free (price == 0)."""
        return self.price == 0

    @property
    def is_upcoming(self):
        """Check if event date is in the future."""
        return self.date > timezone.now()

    @property
    def is_past(self):
        """Check if event date has passed."""
        return self.date <= timezone.now()

    @property
    def seats_remaining(self):
        """Calculate remaining seats by counting confirmed registrations."""
        confirmed = self.registrations.filter(status='confirmed').count()
        return max(0, self.max_capacity - confirmed)

    @property
    def seats_taken(self):
        """Count confirmed registrations."""
        return self.registrations.filter(status='confirmed').count()

    @property
    def is_full(self):
        """Check if event has no remaining seats."""
        return self.seats_remaining == 0

    @property
    def seats_percentage(self):
        """Percentage of seats filled (for progress bar)."""
        if self.max_capacity == 0:
            return 100
        return min(100, int((self.seats_taken / self.max_capacity) * 100))

    @property
    def price_display(self):
        """Return formatted price string."""
        if self.is_free:
            return 'Free'
        return f'₹{self.price:,.0f}'
