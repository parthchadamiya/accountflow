from django.db import models
from django.conf import settings


class Transaction(models.Model):
    TYPE_CHOICES = [('CREDIT', 'Credit'), ('DEBIT', 'Debit')]

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender_client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE,
        related_name='sent_transactions'
    )
    receiver_client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE,
        related_name='received_transactions'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_transactions'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.transaction_date})"
