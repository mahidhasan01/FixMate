from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ( CustomerIDForm, CustomerProfileForm, CustomerSignUpForm, UserUpdateForm, WorkerProfileForm,WorkerSignUpForm, WorkerVerificationForm)
from .models import CustomerProfile, User, WorkerVerification


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


@login_required
def id_verification(request):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    customer = request.user.customer_profile
    can_submit = customer.verification_status in (CustomerProfile.NOT_SUBMITTED, CustomerProfile.REJECTED)

    if request.method == 'POST' and can_submit:
        form = CustomerIDForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.verification_status = CustomerProfile.PENDING
            customer.save()
            messages.success(request, 'Your ID has been sent. We will check it soon.')
            return redirect('accounts_app:profile')
    else:
        form = CustomerIDForm(instance=customer)

    context = {'customer': customer, 'form': form, 'can_submit': can_submit}
    return render(request, 'accounts_app/id_verification.html', context)


@login_required
def worker_verification(request):
    if request.user.role != User.WORKER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    worker = request.user.worker_profile
    attempts = worker.verifications.order_by('-submitted_date')
    has_pending = attempts.filter(verification_status=WorkerVerification.PENDING).exists()
    can_submit = not worker.verified_badge and not has_pending

    if request.method == 'POST' and can_submit:
        form = WorkerVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.worker = worker
            verification.save()
            messages.success(request, 'Your document has been sent. We will check it soon.')
            return redirect('accounts_app:worker_verification')
    else:
        form = WorkerVerificationForm()

    context = {'worker': worker, 'attempts': attempts, 'form': form, 'can_submit': can_submit}
    return render(request, 'accounts_app/worker_verification.html', context)
