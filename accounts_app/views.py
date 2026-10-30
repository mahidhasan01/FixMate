from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

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


@login_required
def verification_queue(request):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    customers = CustomerProfile.objects.filter(verification_status=CustomerProfile.PENDING)
    worker_attempts = WorkerVerification.objects.filter(
        verification_status=WorkerVerification.PENDING
    ).order_by('submitted_date')

    context = {'customers': customers, 'worker_attempts': worker_attempts}
    return render(request, 'accounts_app/verification_queue.html', context)


@login_required
def review_customer_id(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        customer = get_object_or_404(CustomerProfile, pk=pk)
        if request.POST.get('action') == 'approve':
            customer.verification_status = CustomerProfile.APPROVED
            messages.success(request, f'{customer.user.username} ID approved.')
        else:
            customer.verification_status = CustomerProfile.REJECTED
            messages.success(request, f'{customer.user.username} ID rejected.')
        customer.save()

    return redirect('accounts_app:verification_queue')


@login_required
def review_worker_verification(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        verification = get_object_or_404(WorkerVerification, pk=pk)
        username = verification.worker.user.username
        if request.POST.get('action') == 'approve':
            verification.approve_verification()
            messages.success(request, f'{username} is now verified.')
        else:
            verification.reject_verification(request.POST.get('comment', ''))
            messages.success(request, f'{username} document rejected.')

    return redirect('accounts_app:verification_queue')


@login_required
def customer_id_photo(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    customer = get_object_or_404(CustomerProfile, pk=pk)
    return FileResponse(customer.id_photo.open('rb'))


@login_required
def worker_document(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    verification = get_object_or_404(WorkerVerification, pk=pk)
    return FileResponse(verification.document_photo.open('rb'))
