from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from clients.models import Client
from transactions.models import Transaction
from django.db.models import Sum


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        total_clients = Client.objects.filter(status='ACTIVE').count()
        total_debit = Transaction.objects.filter(type='DEBIT').aggregate(total=Sum('amount'))['total'] or 0
        total_credit = Transaction.objects.filter(type='CREDIT').aggregate(total=Sum('amount'))['total'] or 0
        balance = total_credit - total_debit
        recent_transactions = Transaction.objects.select_related(
            'sender_client', 'receiver_client', 'created_by'
        ).order_by('-created_at')[:10]

        context = {
            'total_clients': total_clients,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balance': balance,
            'recent_transactions': recent_transactions,
            'total_transactions': Transaction.objects.count(),
        }
        return render(request, 'dashboard/dashboard.html', context)
