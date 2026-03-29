# ============================================================
# File: events/views.py
# Django Event Management System — Events App Views
# Skills Applied: django-backend + ui-ux-pro-max
# Rules: FBVs only. @login_required on protected views.
#        @staff_required on admin CRUD. Every function commented.
#        Django ORM only — no raw SQL.
# ============================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse

from .models import Event, Category
from .forms import EventForm, EventSearchForm
from users.decorators import staff_required


# ── PUBLIC VIEWS ─────────────────────────────────────────────

def event_list(request):
    """
    Public homepage — shows all published, upcoming events.
    Supports: search (title/description/location), category filter,
              price filter (free/paid), and sort order.
    Paginated: 9 events per page (3-column grid).
    """
    # Start with only published events
    events = Event.objects.filter(
        status=Event.STATUS_PUBLISHED
    ).select_related('category', 'organizer').prefetch_related('registrations')

    # Separate featured events for hero section
    featured_events = events.filter(is_featured=True)[:3]

    # Initialize search form with GET data
    form = EventSearchForm(request.GET)

    # ── Apply Filters ─────────────────────────────────────────
    if form.is_valid():
        # Text search: title, description, location
        query = form.cleaned_data.get('q')
        if query:
            events = events.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(short_description__icontains=query)
            )

        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            events = events.filter(category=category)

        # Price filter
        price_filter = form.cleaned_data.get('price_filter')
        if price_filter == 'free':
            events = events.filter(price=0)
        elif price_filter == 'paid':
            events = events.filter(price__gt=0)

        # Sort order (default: upcoming first)
        sort = form.cleaned_data.get('sort') or 'date'
        events = events.order_by(sort)
    else:
        events = events.order_by('date')

    # ── Upcoming vs Past split ────────────────────────────────
    now = timezone.now()
    upcoming_events = events.filter(date__gte=now)
    past_events = events.filter(date__lt=now)

    # Paginate upcoming events (9 per page)
    paginator = Paginator(upcoming_events, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # All categories for filter dropdown
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'featured_events': featured_events,
        'past_events': past_events[:3],  # Show last 3 past events
        'categories': categories,
        'search_form': form,
        'total_events': upcoming_events.count(),
        'search_query': request.GET.get('q', ''),
        'active_category': request.GET.get('category', ''),
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, slug):
    """
    Public event detail page.
    Shows full event info, countdown timer, seats indicator.
    Checks if current user is already registered.
    """
    event = get_object_or_404(
        Event,
        slug=slug,
        status=Event.STATUS_PUBLISHED
    )

    # Check if the logged-in user has already registered
    user_registration = None
    if request.user.is_authenticated:
        from registrations.models import Registration
        user_registration = Registration.objects.filter(
            event=event,
            email=request.user.email,
            status__in=['confirmed', 'pending']
        ).first()

    # Related events (same category, upcoming, excluding current)
    related_events = Event.objects.filter(
        status=Event.STATUS_PUBLISHED,
        category=event.category,
        date__gte=timezone.now()
    ).exclude(pk=event.pk).select_related('category')[:3]

    context = {
        'event': event,
        'user_registration': user_registration,
        'related_events': related_events,
        'can_register': (
            not event.is_full and
            event.is_upcoming and
            not user_registration and
            event.status == Event.STATUS_PUBLISHED
        ),
    }
    return render(request, 'events/event_detail.html', context)


# ── ADMIN CRUD VIEWS ─────────────────────────────────────────

@staff_required
def event_create(request):
    """
    Admin: Create a new event.
    GET  → Show blank EventForm.
    POST → Validate and save new event, redirect to event list.
    Requires is_staff=True via @staff_required decorator.
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Auto-assign organizer
            event.save()
            messages.success(
                request,
                f'✅ Event "{event.title}" created successfully!'
            )
            return redirect('events:event_detail', slug=event.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {
        'form': form,
        'action': 'Create',
        'title': 'Create New Event',
    })


@staff_required
def event_edit(request, slug):
    """
    Admin: Edit an existing event.
    GET  → Show EventForm pre-filled with existing data.
    POST → Validate and save changes.
    Requires is_staff=True via @staff_required decorator.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'✅ Event "{event.title}" updated successfully!'
            )
            return redirect('events:event_detail', slug=event.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {
        'form': form,
        'event': event,
        'action': 'Edit',
        'title': f'Edit: {event.title}',
    })


@staff_required
def event_delete(request, slug):
    """
    Admin: Delete an event after confirmation.
    GET  → Show confirmation page (ui-ux-pro-max: confirmation before delete).
    POST → Delete event and redirect to event list.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'🗑️ Event "{title}" has been deleted.')
        return redirect('events:event_list')

    return render(request, 'events/event_confirm_delete.html', {
        'event': event
    })


@staff_required
def event_manage_list(request):
    """
    Admin: List ALL events (all statuses) for management.
    Includes draft, published, cancelled, completed events.
    Separate from public event_list which only shows published.
    """
    events = Event.objects.all().select_related(
        'category', 'organizer'
    ).prefetch_related('registrations').order_by('-created_at')

    # Search filter for admin list
    query = request.GET.get('q', '')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query)
        )

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        events = events.filter(status=status_filter)

    paginator = Paginator(events, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'status_choices': Event.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': query,
        'total': events.count(),
    }
    return render(request, 'events/event_manage_list.html', context)


def event_categories(request):
    """
    Public: Show all event categories with event counts.
    Used for browse-by-category UI.
    """
    categories = Category.objects.all().prefetch_related('events')
    return render(request, 'events/categories.html', {
        'categories': categories
    })
