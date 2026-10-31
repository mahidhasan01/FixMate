from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.models import User

from .forms import ServiceListingForm
from .models import ServiceListing


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
        if service_listing.service_image:
            service_listing.service_image.delete(save=False)
        service_listing.delete()
        messages.success(request, 'Listing deleted.')

    return redirect('services_app:my_listings')
