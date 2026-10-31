from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.models import User, WorkerProfile

from .forms import ServiceListingForm
from .models import ServiceCategory, ServiceListing


def listing_list(request):
    listings = ServiceListing.objects.select_related('worker__user', 'category').order_by('-id')

    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if q:
        listings = listings.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category.isdigit():
        listings = listings.filter(category_id=category)
    if min_price.isdigit():
        listings = listings.filter(price__gte=min_price)
    if max_price.isdigit():
        listings = listings.filter(price__lte=max_price)

    context = {
        'listings': listings,
        'categories': ServiceCategory.objects.order_by('name'),
        'q': q,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'services_app/listing_list.html', context)


def listing_detail(request, pk):
    service_listing = get_object_or_404(ServiceListing, pk=pk)
    return render(request, 'services_app/listing_detail.html', {'service_listing': service_listing})


def worker_profile(request, pk):
    worker = get_object_or_404(WorkerProfile, pk=pk)
    listings = worker.listings.order_by('-id')
    return render(request, 'services_app/worker_profile.html', {'worker': worker, 'listings': listings})


@login_required
def my_listings(request):
    if request.user.role != User.WORKER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    listings = request.user.worker_profile.listings.order_by('-id')
    return render(request, 'services_app/my_listings.html', {'listings': listings})


@login_required
def listing_create(request):
    if request.user.role != User.WORKER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    worker = request.user.worker_profile
    if not worker.verified_badge:
        messages.error(request, 'Only verified workers can add listings.')
        return redirect('services_app:my_listings')

    if request.method == 'POST':
        form = ServiceListingForm(request.POST, request.FILES)
        if form.is_valid():
            service_listing = form.save(commit=False)
            service_listing.worker = worker
            service_listing.save()
            messages.success(request, 'Listing added.')
            return redirect('services_app:my_listings')
    else:
        form = ServiceListingForm()

    return render(request, 'services_app/listing_create.html', {'form': form})


@login_required
def listing_update(request, pk):
    service_listing = get_object_or_404(ServiceListing, pk=pk)
    if service_listing.worker.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    old_image_name = service_listing.service_image.name

    if request.method == 'POST':
        form = ServiceListingForm(request.POST, request.FILES, instance=service_listing)
        if form.is_valid():
            form.save()
            if 'service_image' in form.changed_data and old_image_name:
                service_listing.service_image.storage.delete(old_image_name)
            messages.success(request, 'Listing updated.')
            return redirect('services_app:my_listings')
    else:
        form = ServiceListingForm(instance=service_listing)

    return render(request, 'services_app/listing_update.html', {'form': form, 'service_listing': service_listing})


@login_required
def listing_delete(request, pk):
    service_listing = get_object_or_404(ServiceListing, pk=pk)
    if service_listing.worker.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        if service_listing.bookings.exists():
            messages.error(request, "This listing has bookings and can't be deleted.")
            return redirect('services_app:my_listings')
        if service_listing.service_image:
            service_listing.service_image.delete(save=False)
        service_listing.delete()
        messages.success(request, 'Listing deleted.')

    return redirect('services_app:my_listings')
