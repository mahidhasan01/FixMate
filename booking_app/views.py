from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.models import CustomerProfile, User
from services_app.models import ServiceListing

from .forms import BookingForm
from .models import Booking


@login_required
def customer_bookings(request):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    bookings = request.user.customer_profile.bookings.order_by('-id')
    return render(request, 'booking_app/bookings.html', {'bookings': bookings})


@login_required
def worker_bookings(request):
    if request.user.role != User.WORKER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    bookings = request.user.worker_profile.bookings.order_by('-id')
    return render(request, 'booking_app/bookings.html', {'bookings': bookings})


@login_required
def booking_create(request, listing_pk):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    service_listing = get_object_or_404(ServiceListing, pk=listing_pk)
    customer = request.user.customer_profile

    if customer.verification_status == CustomerProfile.PENDING:
        messages.error(request, 'Your ID is still being checked. You can book once it is approved.')
        return redirect('services_app:listing_detail', pk=service_listing.pk)
    if customer.verification_status != CustomerProfile.APPROVED:
        messages.error(request, 'Please verify your ID before booking.')
        return redirect('accounts_app:id_verification')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = customer
            booking.service = service_listing
            booking.worker = service_listing.worker
            booking.save()
            messages.success(request, 'Booking request sent.')
            return redirect('booking_app:customer_bookings')
    else:
        form = BookingForm(initial={'location': customer.address})

    context = {'form': form, 'service_listing': service_listing}
    return render(request, 'booking_app/booking_create.html', context)


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    is_customer = booking.customer.user == request.user
    is_worker = booking.worker.user == request.user
    if not (is_customer or is_worker or request.user.is_staff):
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    return render(request, 'booking_app/booking_detail.html', {'booking': booking})


@login_required
def booking_respond(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.worker.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        if booking.status != Booking.PENDING:
            messages.error(request, 'This booking has already been answered.')
        elif request.POST.get('action') == 'accept':
            booking.status = Booking.ACCEPTED
            booking.save()
            messages.success(request, 'Booking accepted.')
        else:
            booking.status = Booking.REJECTED
            booking.save()
            messages.success(request, 'Booking rejected.')

    return redirect('booking_app:booking_detail', pk=booking.pk)


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        if booking.status != Booking.PENDING:
            messages.error(request, "This booking can't be cancelled anymore.")
        else:
            booking.status = Booking.CANCELLED
            booking.save()
            messages.success(request, 'Booking cancelled.')

    return redirect('booking_app:booking_detail', pk=booking.pk)
