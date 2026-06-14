from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from clients.models import Client
from transactions.models import Transaction
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        total_clients = Client.objects.filter(status='ACTIVE').count()
        all_clients = Client.objects.all()

        total_debit = Transaction.objects.filter(type='DEBIT').aggregate(total=Sum('amount'))['total'] or 0
        total_credit = Transaction.objects.filter(type='CREDIT').aggregate(total=Sum('amount'))['total'] or 0
        balance = total_credit - total_debit

        recent_transactions = Transaction.objects.select_related(
            'sender_client', 'receiver_client', 'created_by'
        ).order_by('-created_at')[:10]

        # Monthly chart data (last 6 months)
        months = []
        debit_data = []
        credit_data = []
        for i in range(5, -1, -1):
            d = timezone.now() - timedelta(days=30 * i)
            month_label = d.strftime('%b %Y')
            months.append(month_label)
            month_debit = Transaction.objects.filter(
                type='DEBIT',
                created_at__year=d.year,
                created_at__month=d.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            month_credit = Transaction.objects.filter(
                type='CREDIT',
                created_at__year=d.year,
                created_at__month=d.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            debit_data.append(float(month_debit))
            credit_data.append(float(month_credit))

        context = {
            'total_clients': total_clients,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balance': balance,
            'recent_transactions': recent_transactions,
            'months_json': json.dumps(months),
            'debit_data_json': json.dumps(debit_data),
            'credit_data_json': json.dumps(credit_data),
            'total_transactions': Transaction.objects.count(),
        }
        return render(request, 'dashboard/dashboard.html', context)
