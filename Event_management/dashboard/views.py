# ============================================================
# File: dashboard/views.py
# Django Event Management System — Admin Dashboard
# Skills Applied: django-backend + data-viz
# Rules: FBVs only. @staff_required on all views.
#        Use performant ORM aggregations.
# ============================================================

import csv
from datetime import timedelta
from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from users.decorators import staff_required
from users.models import CustomUser
from events.models import Event
from registrations.models import Registration


@staff_required
def dashboard_home(request):
    """
    Main Admin Dashboard View.
    Calculates KPI metrics, fetches recent activity, and top events.
    Uses efficient ORM queries (Count, select_related).
    """
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # ── 1. KPI Metrics ───────────────────────────────────────
    total_users = CustomUser.objects.count()
    new_users = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()

    # Total published vs draft events
    total_events = Event.objects.count()
    active_events = Event.objects.filter(
        status=Event.STATUS_PUBLISHED,
        date__gte=now
    ).count()

    # Total confirmed registrations
    total_registrations = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED
    ).count()

    # Total Revenue (sum of event.price for confirmed registrations)
    # Excludes free events (where price = 0)
    revenue_aggr = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED
    ).aggregate(total_revenue=Sum('event__price'))
    total_revenue = revenue_aggr['total_revenue'] or 0.00

    # ── 2. Top Events (by confirmed registrations) ───────────
    top_events = Event.objects.annotate(
        reg_count=Count('registrations', filter=Registration.objects.filter(status=Registration.STATUS_CONFIRMED))
    ).order_by('-reg_count')[:5]

    # ── 3. Recent Activity ───────────────────────────────────
    recent_registrations = Registration.objects.select_related(
        'event', 'user', 'ticket'
    ).order_by('-registered_at')[:8]

    context = {
        'total_users': total_users,
        'new_users': new_users,
        'total_events': total_events,
        'active_events': active_events,
        'total_registrations': total_registrations,
        'total_revenue': total_revenue,
        'top_events': top_events,
        'recent_registrations': recent_registrations,
    }
    return render(request, 'dashboard/home.html', context)


@staff_required
def chart_data_api(request):
    """
    JSON API for Chart.js.
    Returns daily registrations and revenue over the last 30 days.
    """
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # Aggregate registrations by day (confirmed only)
    daily_stats = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED,
        registered_at__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('registered_at')
    ).values('day').annotate(
        count=Count('id'),
        revenue=Sum('event__price')
    ).order_by('day')

    # Build the data arrays for the chart
    labels = []
    reg_counts = []
    revenues = []

    # Map the database results into lists
    # Note: For days with 0 registrations, they won't appear in the DB query,
    # so we'll build a complete 30-day timeline and fill in the blanks.
    stats_dict = {
        entry['day']: {'count': entry['count'], 'revenue': float(entry['revenue'] or 0)}
        for entry in daily_stats if entry['day']
    }

    for i in range(30, -1, -1):
        date = (now - timedelta(days=i)).date()
        labels.append(date.strftime('%b %d'))
        if date in stats_dict:
            reg_counts.append(stats_dict[date]['count'])
            revenues.append(stats_dict[date]['revenue'])
        else:
            reg_counts.append(0)
            revenues.append(0.0)

    return JsonResponse({
        'labels': labels,
        'registrations': reg_counts,
        'revenue': revenues
    })


@staff_required
def export_registrations_csv(request):
    """
    Export all confirmed registrations as a CSV download.
    Useful for printing checking lists / importing to Excel.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="eventhub_registrations.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Registration ID', 'Event', 'Event Date', 'Attendee Name', 
        'Email', 'Phone', 'Ticket Number', 'Amount Paid', 'Registered On'
    ])

    registrations = Registration.objects.filter(
        status=Registration.STATUS_CONFIRMED
    ).select_related('event', 'ticket').order_by('-registered_at')

    for reg in registrations:
        ticket_num = reg.ticket.ticket_number_short if getattr(reg, 'ticket', None) else 'N/A'
        writer.writerow([
            reg.id,
            reg.event.title,
            reg.event.date.strftime('%Y-%m-%d %H:%M'),
            reg.name,
            reg.email,
            reg.phone or '',
            ticket_num,
            reg.event.price,
            reg.registered_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response
