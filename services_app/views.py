from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts_app.models import User

from .forms import ServiceListingForm


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
            listing = form.save(commit=False)
            listing.worker = worker
            listing.save()
            messages.success(request, 'Listing added.')
            return redirect('services_app:my_listings')
    else:
        form = ServiceListingForm()

    return render(request, 'services_app/listing_form.html', {'form': form})
