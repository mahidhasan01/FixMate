from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CustomerSignUpForm, WorkerSignUpForm


def choose_role(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts_app/choose_role.html')


def customer_signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FixMate, {user.username}!')
            return redirect('home')
    else:
        form = CustomerSignUpForm()

    return render(request, 'accounts_app/signup.html', {'form': form, 'role': 'customer'})


def worker_signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = WorkerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FixMate, {user.username}!')
            return redirect('home')
    else:
        form = WorkerSignUpForm()

    return render(request, 'accounts_app/signup.html', {'form': form, 'role': 'worker'})
