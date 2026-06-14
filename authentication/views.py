from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View


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
