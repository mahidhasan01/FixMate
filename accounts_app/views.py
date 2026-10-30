from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ( CustomerProfileForm, CustomerSignUpForm, UserUpdateForm, WorkerProfileForm,WorkerSignUpForm)
from .models import User


def choose_role(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts_app/choose_role.html')


@login_required
def after_login(request):
    messages.success(request, f'Welcome back, {request.user.username}!')
    if request.user.is_staff:
        return redirect('admin:index')
    return redirect('home')


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


@login_required
def profile(request):
    user = request.user
    if user.role == User.CUSTOMER:
        role_profile = user.customer_profile
    elif user.role == User.WORKER:
        role_profile = user.worker_profile
    else:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    return render(request, 'accounts_app/profile.html', {'role_profile': role_profile})


@login_required
def profile_edit(request):
    user = request.user
    if user.role == User.CUSTOMER:
        role_profile = user.customer_profile
        profile_form_class = CustomerProfileForm
    elif user.role == User.WORKER:
        role_profile = user.worker_profile
        profile_form_class = WorkerProfileForm
    else:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = profile_form_class(request.POST, request.FILES, instance=role_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts_app:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = profile_form_class(instance=role_profile)

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts_app/profile_edit.html', context)
