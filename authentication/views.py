from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import User


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'authentication/login.html')

    def post(self, request):
        code = request.POST.get('code', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=code, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid code or password. Please try again.')
        return render(request, 'authentication/login.html', {'code': code})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')

    def get(self, request):
        logout(request)
        return redirect('login')


def admin_required(view_func):
    """Decorator: only ADMIN role can access."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            messages.error(request, 'Access denied. Admin role required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator(admin_required, name='dispatch')
class UserListView(View):
    def get(self, request):
        users = User.objects.all().order_by('role', 'name')
        return render(request, 'authentication/user_list.html', {'users': users})


@method_decorator(admin_required, name='dispatch')
class UserCreateView(View):
    def get(self, request):
        return render(request, 'authentication/user_form.html', {'action': 'Create'})

    def post(self, request):
        data = request.POST
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        role = data.get('role', 'STAFF')
        password = data.get('password', '')
        confirm = data.get('confirm_password', '')

        if not code or not name or not password:
            messages.error(request, 'Code, name, and password are required.')
            return render(request, 'authentication/user_form.html', {'action': 'Create', 'data': data})

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/user_form.html', {'action': 'Create', 'data': data})

        if User.objects.filter(code=code).exists():
            messages.error(request, f'User with code "{code}" already exists.')
            return render(request, 'authentication/user_form.html', {'action': 'Create', 'data': data})

        try:
            user = User.objects.create_user(
                code=code,
                password=password,
                name=name,
                email=email,
                role=role,
                is_staff=(role == 'ADMIN'),
            )
            messages.success(request, f'User "{user.name}" ({user.code}) created successfully.')
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'authentication/user_form.html', {'action': 'Create', 'data': data})


@method_decorator(admin_required, name='dispatch')
class UserUpdateView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, 'authentication/user_form.html', {'action': 'Update', 'edit_user': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        data = request.POST
        user.name = data.get('name', '').strip()
        user.email = data.get('email', '').strip()
        user.role = data.get('role', 'STAFF')
        user.is_staff = (user.role == 'ADMIN')

        new_password = data.get('password', '').strip()
        confirm = data.get('confirm_password', '').strip()
        if new_password:
            if new_password != confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'authentication/user_form.html', {'action': 'Update', 'edit_user': user})
            user.set_password(new_password)

        user.save()
        messages.success(request, f'User "{user.name}" updated successfully.')
        return redirect('user_list')


@method_decorator(admin_required, name='dispatch')
class UserDeleteView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('user_list')
        name = user.name
        user.delete()
        messages.success(request, f'User "{name}" deleted.')
        return redirect('user_list')
