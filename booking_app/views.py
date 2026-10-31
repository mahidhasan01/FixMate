from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts_app.models import User


@login_required
def customer_bookings(request):
    if request.user.role != User.CUSTOMER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    bookings = request.user.customer_profile.bookings.order_by('-id')
    return render(request, 'booking_app/customer_bookings.html', {'bookings': bookings})
