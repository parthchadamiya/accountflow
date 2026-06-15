from django.core.management.base import BaseCommand
from authentication.models import User


class Command(BaseCommand):
    help = 'Seed the database with the default admin user'

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
