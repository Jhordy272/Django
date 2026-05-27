from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest

from .models import PlanningTask


def login_view(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def home(request: HttpRequest):
    return render(request, 'index.html')


@login_required(login_url='/login/')
def planning(request: HttpRequest):
    tasks = PlanningTask.objects.all()

    status   = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to   = request.GET.get('date_to')

    if status:
        tasks = tasks.filter(status=status)
    if date_from:
        tasks = tasks.filter(due_date__gte=date_from)
    if date_to:
        tasks = tasks.filter(due_date__lte=date_to)

    return render(request, 'planning.html', {'tasks': tasks})


@login_required(login_url='/login/')
def users(request: HttpRequest):
    all_users = User.objects.all().order_by('username')
    return render(request, 'users.html', {'users': all_users})


@login_required(login_url='/login/')
def user_edit(request: HttpRequest, pk: int):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name  = request.POST.get('last_name', '')
        user.email      = request.POST.get('email', '')
        user.is_active  = request.POST.get('is_active') == '1'
        user.is_staff   = request.POST.get('is_staff') == '1'
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        user.save()
        return redirect('users')
    return render(request, 'users.html', {
        'users': User.objects.all().order_by('username'),
        'edit_user': user,
    })


@login_required(login_url='/login/')
def user_delete(request: HttpRequest, pk: int):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            user.delete()
    return redirect('users')


@login_required(login_url='/login/')
def clients(request: HttpRequest):
    return render(request, 'clients.html')


@login_required(login_url='/login/')
def tax_returns(request: HttpRequest):
    return render(request, 'tax_returns.html')


@login_required(login_url='/login/')
def my_returns(request: HttpRequest):
    return render(request, 'my_returns.html')


@login_required(login_url='/login/')
def configuration(request: HttpRequest):
    return render(request, 'configuration.html')
