from django.core.management.base import BaseCommand
from authentication.models import User
from clients.models import Client
from transactions.models import Transaction
from django.utils import timezone
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seed the database with default data'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(code='ADMIN001').exists():
            User.objects.create_user(
                code='ADMIN001',
                password='Admin@123',
                name='Super Admin',
                role='ADMIN',
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: ADMIN001 / Admin@123'))
        else:
            self.stdout.write('Admin user already exists.')

        # Create sample clients
        clients_data = [
            {'client_name': 'Acme Corporation', 'code': 'C001', 'mobile': '9876543210', 'opening_balance': 50000},
            {'client_name': 'Global Tech Ltd', 'code': 'C002', 'mobile': '9876543211', 'opening_balance': 75000},
            {'client_name': 'StartUp Hub', 'code': 'C003', 'mobile': '9876543212', 'opening_balance': 30000},
            {'client_name': 'Blue Ocean Inc', 'code': 'C004', 'mobile': '9876543213', 'opening_balance': 100000},
            {'client_name': 'Pioneer Solutions', 'code': 'C005', 'mobile': '9876543214', 'opening_balance': 25000},
        ]

        admin = User.objects.get(code='ADMIN001')
        created_clients = []
        for data in clients_data:
            client, created = Client.objects.get_or_create(
                code=data['code'],
                defaults={
                    'client_name': data['client_name'],
                    'mobile': data['mobile'],
                    'opening_balance': data['opening_balance'],
                    'current_balance': data['opening_balance'],
                    'created_by': admin,
                    'updated_by': admin,
                }
            )
            created_clients.append(client)
            if created:
                self.stdout.write(f'Client created: {client.client_name}')

        # Create sample transactions
        if Transaction.objects.count() == 0 and len(created_clients) >= 2:
            transactions = [
                (created_clients[0], created_clients[1], 5000, 'Initial payment'),
                (created_clients[1], created_clients[2], 3000, 'Service fee'),
                (created_clients[2], created_clients[3], 8000, 'Product purchase'),
                (created_clients[3], created_clients[4], 2500, 'Consulting fee'),
                (created_clients[0], created_clients[3], 10000, 'Contract payment'),
            ]
            for sender, receiver, amount, desc in transactions:
                amount = Decimal(amount)
                Transaction.objects.create(
                    amount=amount,
                    type='DEBIT',
                    description=desc,
                    transaction_date=timezone.now().date(),
                    sender_client=sender,
                    receiver_client=receiver,
                    created_by=admin,
                )
                sender.current_balance -= amount
                sender.save()
                receiver.current_balance += amount
                receiver.save()
            self.stdout.write(self.style.SUCCESS('Sample transactions created.'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
