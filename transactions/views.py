from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone
from .models import Transaction
from clients.models import Client
from decimal import Decimal


@method_decorator(login_required, name='dispatch')
class TransactionListView(View):
    def get(self, request):
        transactions = Transaction.objects.select_related(
            'sender_client', 'receiver_client', 'created_by'
        ).order_by('-created_at')
        return render(request, 'transactions/transaction_list.html', {'transactions': transactions})


@method_decorator(login_required, name='dispatch')
class TransactionCreateView(View):
    def get(self, request):
        clients = Client.objects.filter(status='ACTIVE').order_by('client_name')
        return render(request, 'transactions/transaction_form.html', {'clients': clients})

    def post(self, request):
        data = request.POST
        sender_id = data.get('sender_client')
        receiver_id = data.get('receiver_client')
        amount = Decimal(data.get('amount', 0))
        description = data.get('description', '')
        transaction_date = data.get('transaction_date') or timezone.now().date()

        if sender_id == receiver_id:
            messages.error(request, 'Sender and receiver cannot be the same client.')
            clients = Client.objects.filter(status='ACTIVE')
            return render(request, 'transactions/transaction_form.html', {'clients': clients})

        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
            clients = Client.objects.filter(status='ACTIVE')
            return render(request, 'transactions/transaction_form.html', {'clients': clients})

        sender = get_object_or_404(Client, pk=sender_id)
        receiver = get_object_or_404(Client, pk=receiver_id)

        # Warn if balance goes negative but allow the transaction (overdraft allowed)
        will_go_negative = sender.current_balance < amount

        Transaction.objects.create(
            amount=amount,
            type='DEBIT',
            description=description,
            transaction_date=transaction_date,
            sender_client=sender,
            receiver_client=receiver,
            created_by=request.user,
        )

        sender.current_balance -= amount
        sender.save()
        receiver.current_balance += amount
        receiver.save()

        if will_go_negative:
            messages.warning(
                request,
                f'Transaction created. Note: {sender.client_name}\'s balance is now ₹{sender.current_balance:.2f} '
                f'(negative — this client now appears on the DR side of Trial Balance).'
            )
        else:
            messages.success(request, f'Transfer of ₹{amount} from {sender.client_name} to {receiver.client_name} completed.')

        return redirect('transaction_list')


@method_decorator(login_required, name='dispatch')
class TransactionDetailView(View):
    def get(self, request, pk):
        transaction = get_object_or_404(
            Transaction.objects.select_related('sender_client', 'receiver_client', 'created_by'),
            pk=pk
        )
        return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})
