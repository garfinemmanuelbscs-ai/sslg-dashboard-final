from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from .models import Event

# ==========================================
# 🔐 GRANULAR EVENT SECURITY CONTROLLERS
# ==========================================

def is_admin_user(user):
    """Checks for root administrator status"""
    return user.is_superuser or user.username.lower() == 'admin'

def has_event_perm(user, perm_codename):
    """Evaluates explicit, superuser, or group role permissions strictly for the events app"""
    if not user or user.is_anonymous:
        return False
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm(f'events.{perm_codename}') or
        user.groups.filter(
            permissions__content_type__app_label='events', 
            permissions__codename=perm_codename
        ).exists()
    )

# 🌟 Granular operational clearance gates
def can_add_events(user):
    return is_admin_user(user) or has_event_perm(user, 'add_event')

def can_change_events(user):
    return is_admin_user(user) or has_event_perm(user, 'change_event')

def can_delete_events(user):
    return is_admin_user(user) or has_event_perm(user, 'delete_event')

def can_view_events(user):
    return (
        is_admin_user(user) or 
        has_event_perm(user, 'view_event') or 
        has_event_perm(user, 'add_event') or 
        has_event_perm(user, 'change_event') or 
        has_event_perm(user, 'delete_event')
    )

def can_print_events(user):
    """🛡️ Guardrail: Only allows roles with explicit printing permissions to see the summary print matrix"""
    return is_admin_user(user) or has_event_perm(user, 'print_event')


# ==========================================
# 🏛️ EVENTS CORE MANAGEMENT MODULE
# ==========================================

@login_required
@user_passes_test(can_view_events, login_url='dashboard')
def events_dashboard(request):
    """📊 Analytics Dashboard & Event Registry Tracking Panel"""
    is_modifier = can_add_events(request.user) or can_change_events(request.user)
    
    # 📈 Real-Time Master Events Processing
    events_queryset = Event.objects.all().order_by('-date')
    
    total_budget = events_queryset.aggregate(Sum('budget'))['budget__sum'] or Decimal('0.00')
    total_expense = events_queryset.aggregate(Sum('actual_expense'))['actual_expense__sum'] or Decimal('0.00')
    total_participants = events_queryset.aggregate(Sum('participants'))['participants__sum'] or 0
    financial_variance = total_budget - total_expense

    for event in events_queryset:
        if event.actual_expense is not None:
            event.variance = event.budget - event.actual_expense
            event.burn_rate = (event.actual_expense / event.budget) * 100 if event.budget > 0 else 0
        else:
            event.variance = None
            event.burn_rate = 0

    return render(request, 'events/event_dashboard.html', {
        'events': events_queryset,
        'total_budget': total_budget,
        'total_expense': total_expense,
        'total_participants': total_participants,
        'financial_variance': financial_variance,
        'is_modifier': is_modifier,
        'can_add': can_add_events(request.user)
    })


@login_required
def create_event(request):
    """📝 Form handling to initialize and store new event records"""
    if not can_add_events(request.user):
        messages.error(request, "🛡️ Access Denied: Your profile lacks 'add_event' operational clearances.")
        return redirect('events_calendar')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '').strip()
        date = request.POST.get('date')
        venue = request.POST.get('venue')
        budget = request.POST.get('budget')
        actual_expense = request.POST.get('actual_expense')
        participants = request.POST.get('participants', 0)

        try:
            budget_val = Decimal(budget) if budget else Decimal('0.00')
            expense_val = Decimal(actual_expense) if actual_expense else None
            participant_count = int(participants) if participants else 0

            Event.objects.create(
                title=title,
                description=description,
                date=date,
                venue=venue,
                budget=budget_val,
                actual_expense=expense_val,
                participants=participant_count
            )
            messages.success(request, f"🎉 Management tracker for '{title}' deployed successfully!")
        except Exception as e:
            messages.error(request, f"Configuration Fault: Failed to initialize event matrix profile: {e}")
            
    return redirect('events_calendar')


@login_required
def update_expense(request, event_id):
    """💸 Quick-action modifier to balance sheets post-event"""
    if not can_change_events(request.user):
        messages.error(request, "🛡️ Access Denied: Your profile lacks 'change_event' optimization clearances.")
        return redirect('events_calendar')

    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        expense = request.POST.get('actual_expense')
        participants = request.POST.get('participants')

        try:
            if expense:
                event.actual_expense = Decimal(expense)
            if participants:
                event.participants = int(participants)
            event.save()
            messages.success(request, f"Financial indices optimized for event: {event.title}")
        except Exception as e:
            messages.error(request, f"Adjustment Error: Could not overwrite balance entries: {e}")

    return redirect('events_calendar')


@login_required
def delete_event(request, event_id):
    """🗑️ System Guardrail: Drops an event completely from the ledger"""
    if not can_delete_events(request.user):
        messages.error(request, "🛡️ Access Denied: Emergency data purge requires 'delete_event' authorization.")
        return redirect('events_calendar')

    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        title = event.title
        event.delete()
        messages.success(request, f"Event model file '{title}' purged cleanly from registry.")
    return redirect('events_calendar')


# ==========================================
# 🖨️ SYSTEM PRINT GENERATION TERMINALS
# ==========================================

@login_required
@user_passes_test(can_print_events, login_url='events_dashboard')
def print_events_summary(request):
    """🖨️ Generates print-optimized historical event and expense logs via strict matrix gate controls"""
    events_queryset = Event.objects.all().order_by('date')
    return render(request, 'events/print_summary.html', {'events': events_queryset})