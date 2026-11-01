from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts_app.models import CustomerProfile, User
from services_app.models import ServiceListing

from .forms import BookingForm, CompletionPhotoForm, ReviewForm
from .models import Booking, FraudAnomalyFlag, JobVerification, Review
from . import fraud


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
            fraud.check_cancels(booking.customer)
            messages.success(request, 'Booking cancelled.')

    return redirect('booking_app:booking_detail', pk=booking.pk)


@login_required
def completion_upload(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.worker.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if booking.status != Booking.ACCEPTED:
        messages.error(request, 'You can only send a photo for an accepted booking.')
        return redirect('booking_app:booking_detail', pk=booking.pk)

    job = JobVerification.objects.filter(booking=booking).first()
    if job and job.verification_status != JobVerification.REJECTED:
        messages.error(request, 'You have already sent a photo for this booking.')
        return redirect('booking_app:booking_detail', pk=booking.pk)

    old_photo_name = job.completion_photo.name if job else ''

    if request.method == 'POST':
        form = CompletionPhotoForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.booking = booking
            job.verification_status = JobVerification.PENDING
            job.save()
            if old_photo_name:
                job.completion_photo.storage.delete(old_photo_name)
            messages.success(request, 'Photo sent. The customer will check it.')
            return redirect('booking_app:booking_detail', pk=booking.pk)
    else:
        form = CompletionPhotoForm()

    return render(request, 'booking_app/completion_form.html', {'form': form, 'booking': booking})


@login_required
def completion_review(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        job = JobVerification.objects.filter(booking=booking).first()
        if not job or job.verification_status != JobVerification.PENDING:
            messages.error(request, 'There is no photo waiting for your review.')
        elif request.POST.get('action') == 'approve':
            has_payment = booking.payments.filter(payment_status__in=['pending', 'paid']).exists()
            if has_payment:
                job.approve_completion()
                messages.success(request, 'Job approved. The booking is now completed.')
            else:
                messages.error(request, 'Please pay for this booking before approving the job.')
        else:
            job.reject_completion()
            fraud.check_rejected_photo(booking)
            messages.success(request, 'Photo rejected. The worker can send a new one.')

    return redirect('booking_app:booking_detail', pk=booking.pk)


@login_required
def review_create(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if booking.status != Booking.COMPLETED:
        messages.error(request, 'You can review a booking only after it is completed.')
        return redirect('booking_app:booking_detail', pk=booking.pk)
    if Review.objects.filter(booking=booking).exists():
        messages.error(request, 'You have already reviewed this booking.')
        return redirect('booking_app:booking_detail', pk=booking.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.customer = booking.customer
            review.worker = booking.worker
            review.save()
            fraud.check_bad_ratings(review.worker)
            fraud.check_fake_reviews(review)
            messages.success(request, 'Thanks for your review.')
            return redirect('booking_app:booking_detail', pk=booking.pk)
    else:
        form = ReviewForm()

    return render(request, 'booking_app/review_create.html', {'form': form, 'booking': booking})


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            fraud.check_bad_ratings(review.worker)
            fraud.check_fake_reviews(review)
            messages.success(request, 'Review updated.')
            return redirect('booking_app:booking_detail', pk=review.booking.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'booking_app/review_update.html', {'form': form, 'review': review})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')

    return redirect('booking_app:booking_detail', pk=review.booking.pk)


@login_required
def flag_list(request):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    open_flags = FraudAnomalyFlag.objects.filter(flag_status=FraudAnomalyFlag.OPEN).order_by('-risk_score', '-created_date')
    closed_flags = FraudAnomalyFlag.objects.exclude(flag_status=FraudAnomalyFlag.OPEN).order_by('-created_date')[:20]
    context = {'open_flags': open_flags, 'closed_flags': closed_flags}
    return render(request, 'booking_app/flag_list.html', context)


@login_required
def flag_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if request.method == 'POST':
        flag = get_object_or_404(FraudAnomalyFlag, pk=pk)
        if request.POST.get('action') == 'resolve':
            flag.flag_status = FraudAnomalyFlag.RESOLVED
            messages.success(request, 'Flag marked as resolved.')
        else:
            flag.flag_status = FraudAnomalyFlag.DISMISSED
            messages.success(request, 'Flag dismissed.')
        flag.save()

    return redirect('booking_app:flag_list')


@login_required
def dashboard(request):
    user = request.user
    if user.role == User.CUSTOMER:
        profile = user.customer_profile
        bookings = profile.bookings
        context = {
            'id_approved': profile.verification_status == CustomerProfile.APPROVED,
            'photos_to_review': bookings.filter(job_verification__verification_status=JobVerification.PENDING),
            'upcoming': bookings.filter(status=Booking.ACCEPTED).order_by('booking_date'),
        }
    elif user.role == User.WORKER:
        profile = user.worker_profile
        bookings = profile.bookings
        context = {
            'is_verified': profile.verified_badge,
            'new_requests': bookings.filter(status=Booking.PENDING).order_by('booking_date'),
            'need_photo': bookings.filter(status=Booking.ACCEPTED).exclude(
                job_verification__verification_status=JobVerification.PENDING
            ),
        }
    else:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    context['pending_count'] = bookings.filter(status=Booking.PENDING).count()
    context['accepted_count'] = bookings.filter(status=Booking.ACCEPTED).count()
    context['completed_count'] = bookings.filter(status=Booking.COMPLETED).count()
    return render(request, 'booking_app/dashboard.html', context)
