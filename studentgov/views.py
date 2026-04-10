from django.shortcuts import render
from finance.models import Transaction
from inventory.models import Item
from attendance.models import AttendanceRecord
from events.models import Event
from django.db.models import Sum

def dashboard(request):
    # Finance summary
    income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expense

    # Inventory alerts
    low_stock_items = Item.objects.filter(quantity__lt=5)

    # Attendance summary
    absences = AttendanceRecord.objects.filter(status='absent').count()

    # Upcoming events
    upcoming_events = Event.objects.order_by('date')[:5]

    context = {
        'balance': balance,
        'low_stock_items': low_stock_items,
        'absences': absences,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'dashboard.html', context)
