from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from booking_app.models import Booking

from .forms import PaymentForm
from .models import Payment

RECEIVING_NUMBER = '01811957773'

CASHOUT_RATES = {
    Payment.NAGAD: Decimal('0.01299'),
    Payment.ROCKET: Decimal('0.0167'),
    Payment.BKASH: Decimal('0.0185'),
}


def amount_to_send(price, method):
    rate = CASHOUT_RATES.get(method, 0)
    return round(price + price * rate, 2)


@login_required
def checkout(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk)
    if booking.customer.user != request.user:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    if booking.status != Booking.ACCEPTED:
        messages.error(request, 'You can pay only after the worker accepts the booking.')
        return redirect('booking_app:booking_detail', pk=booking.pk)
    if booking.payments.filter(payment_status__in=[Payment.PENDING, Payment.PAID]).exists():
        messages.error(request, 'You have already paid for this booking.')
        return redirect('booking_app:booking_detail', pk=booking.pk)

    price = booking.service.price

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = amount_to_send(price, payment.payment_method)
            payment.save()
            messages.success(request, "Payment submitted. We'll confirm it soon.")
            return redirect('booking_app:booking_detail', pk=booking.pk)
    else:
        form = PaymentForm()

    context = { 'booking': booking, 'form': form, 'receiving_number': RECEIVING_NUMBER,
                'nagad_total': amount_to_send(price, Payment.NAGAD),
                'rocket_total': amount_to_send(price, Payment.ROCKET),
                'bkash_total': amount_to_send(price, Payment.BKASH),
    }
    return render(request, 'payment_app/checkout.html', context)
