from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from .models import Client


@method_decorator(login_required, name='dispatch')
class ClientListView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        clients = Client.objects.all()
        if query:
            clients = clients.filter(client_name__icontains=query) | clients.filter(code__icontains=query)
        return render(request, 'clients/client_list.html', {'clients': clients, 'query': query})


@method_decorator(login_required, name='dispatch')
class ClientCreateView(View):
    def get(self, request):
        return render(request, 'clients/client_form.html', {'action': 'Create'})

    def post(self, request):
        data = request.POST
        try:
            client = Client.objects.create(
                client_name=data['client_name'],
                code=data['code'].upper(),
                mobile=data.get('mobile', ''),
                email=data.get('email', ''),
                address=data.get('address', ''),
                opening_balance=data.get('opening_balance') or 0,
                current_balance=data.get('opening_balance') or 0,
                status=data.get('status', 'ACTIVE'),
                created_by=request.user,
                updated_by=request.user,
            )
            messages.success(request, f'Client "{client.client_name}" created successfully.')
            return redirect('client_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            # Pass POST values as a plain dict so the template can repopulate fields
            return render(request, 'clients/client_form.html', {
                'action': 'Create',
                'prefill': {
                    'client_name': data.get('client_name', ''),
                    'code': data.get('code', ''),
                    'mobile': data.get('mobile', ''),
                    'email': data.get('email', ''),
                    'address': data.get('address', ''),
                    'opening_balance': data.get('opening_balance', ''),
                    'status': data.get('status', 'ACTIVE'),
                },
            })


@method_decorator(login_required, name='dispatch')
class ClientDetailView(View):
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        sent = client.sent_transactions.select_related('receiver_client').order_by('-created_at')[:10]
        received = client.received_transactions.select_related('sender_client').order_by('-created_at')[:10]
        return render(request, 'clients/client_detail.html', {
            'client': client, 'sent': sent, 'received': received
        })


@method_decorator(login_required, name='dispatch')
class ClientUpdateView(View):
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        return render(request, 'clients/client_form.html', {'action': 'Update', 'client': client})

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        data = request.POST
        try:
            client.client_name = data['client_name']
            client.code = data['code'].upper()
            client.mobile = data.get('mobile', '')
            client.email = data.get('email', '')
            client.address = data.get('address', '')
            client.status = data.get('status', 'ACTIVE')
            client.updated_by = request.user
            client.save()
            messages.success(request, f'Client "{client.client_name}" updated successfully.')
            return redirect('client_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'clients/client_form.html', {'action': 'Update', 'client': client})


@method_decorator(login_required, name='dispatch')
class ClientDeleteView(View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        name = client.client_name
        client.delete()
        messages.success(request, f'Client "{name}" deleted successfully.')
        return redirect('client_list')
