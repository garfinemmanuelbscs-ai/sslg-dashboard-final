from django.contrib import admin
from .models import Item

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'condition', 'custodian', 'date_added')
    list_filter = ('condition', 'custodian')
    search_fields = ('name', 'custodian')
    ordering = ('-date_added',)

admin.site.register(Item, ItemAdmin)