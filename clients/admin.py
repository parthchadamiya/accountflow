from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code', 'client_name', 'mobile', 'opening_balance', 'current_balance', 'status')
    list_filter = ('status',)
    search_fields = ('code', 'client_name', 'mobile')
