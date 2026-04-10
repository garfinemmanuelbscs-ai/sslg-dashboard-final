from django.contrib import admin
from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'budget', 'actual_expense', 'participants')
    list_filter = ('date', 'venue')
    search_fields = ('title', 'venue')
    ordering = ('-date',)

admin.site.register(Event, EventAdmin)
