from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('source', 'type', 'amount', 'date', 'officer')
    list_filter = ('type', 'date')
    search_fields = ('source', 'officer__username')

admin.site.register(Transaction, TransactionAdmin)