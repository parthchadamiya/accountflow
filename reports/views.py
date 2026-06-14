from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from clients.models import Client
from transactions.models import Transaction
from django.db.models import Sum, Q
from decimal import Decimal
from itertools import zip_longest
import datetime


@method_decorator(login_required, name='dispatch')
class TrialBalanceView(View):
    def get(self, request):
        clients = Client.objects.all().order_by('client_name')

        cr_rows = []  # positive balance (credit side)
        dr_rows = []  # negative balance (debit side)
        total_cr = Decimal('0')
        total_dr = Decimal('0')

        for client in clients:
            bal = client.current_balance
            if bal >= 0:
                cr_rows.append({'code': client.code, 'name': client.client_name, 'balance': bal})
                total_cr += bal
            else:
                dr_rows.append({'code': client.code, 'name': client.client_name, 'balance': abs(bal)})
                total_dr += abs(bal)

        # Zip DR (left/negative) and CR (right/positive) side-by-side
        paired_rows = list(zip_longest(dr_rows, cr_rows, fillvalue=None))

        context = {
            'paired_rows': paired_rows,
            'total_cr': total_cr,
            'total_dr': total_dr,
            'cr_count': len(cr_rows),
            'dr_count': len(dr_rows),
            'difference': total_cr - total_dr,
        }
        return render(request, 'reports/trial_balance.html', context)


@method_decorator(login_required, name='dispatch')
class PartyLedgerView(View):
    def get(self, request):
        code = request.GET.get('code', '').strip().upper()
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        client = None
        ledger_rows = []
        opening_balance = Decimal('0')
        closing_balance = Decimal('0')
        total_credit = Decimal('0')
        total_debit = Decimal('0')
        error = None
        searched = bool(code and start_date and end_date)

        all_clients = Client.objects.order_by('client_name')

        if searched:
            try:
                client = Client.objects.get(code=code)
            except Client.DoesNotExist:
                error = f'No client found with code "{code}".'
                searched = False

        if client and start_date and end_date:
            try:
                sd = datetime.date.fromisoformat(start_date)
                ed = datetime.date.fromisoformat(end_date)
            except ValueError:
                error = 'Invalid date format.'
                searched = False
            else:
                # Opening balance = opening_balance + all transactions BEFORE start_date
                before_received = Transaction.objects.filter(
                    receiver_client=client,
                    transaction_date__lt=sd
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                before_sent = Transaction.objects.filter(
                    sender_client=client,
                    transaction_date__lt=sd
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

                opening_balance = client.opening_balance + before_received - before_sent

                # Transactions in date range (both as sender and receiver)
                txs_in_range = Transaction.objects.filter(
                    Q(sender_client=client) | Q(receiver_client=client),
                    transaction_date__gte=sd,
                    transaction_date__lte=ed,
                ).select_related('sender_client', 'receiver_client').order_by('transaction_date', 'id')

                running_balance = opening_balance

                for tx in txs_in_range:
                    if tx.receiver_client == client:
                        # Money came in → credit
                        credit = tx.amount
                        debit = Decimal('0')
                        party = tx.sender_client.client_name
                        remarks = tx.description or 'RCV'
                    else:
                        # Money went out → debit
                        credit = Decimal('0')
                        debit = tx.amount
                        party = tx.receiver_client.client_name
                        remarks = tx.description or 'PAID'

                    running_balance = running_balance + credit - debit
                    total_credit += credit
                    total_debit += debit

                    ledger_rows.append({
                        'date': tx.transaction_date,
                        'id': tx.id,
                        'credit': credit,
                        'debit': debit,
                        'balance': running_balance,
                        'party': party,
                        'remarks': remarks,
                    })

                closing_balance = running_balance

        context = {
            'client': client,
            'all_clients': all_clients,
            'code': code,
            'start_date': start_date,
            'end_date': end_date,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'total_credit': total_credit,
            'total_debit': total_debit,
            'ledger_rows': ledger_rows,
            'error': error,
            'searched': searched,
        }
        return render(request, 'reports/party_ledger.html', context)
