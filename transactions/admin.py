from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'amount', 'sender_client', 'receiver_client', 'transaction_date', 'created_at')
    list_filter = ('type', 'transaction_date')
    search_fields = ('sender_client__client_name', 'receiver_client__client_name')
