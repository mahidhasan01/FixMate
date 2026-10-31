from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts_app.models import User


@login_required
def my_listings(request):
    if request.user.role != User.WORKER:
        messages.error(request, "You don't have access to that page.")
        return redirect('home')

    listings = request.user.worker_profile.listings.order_by('-id')
    return render(request, 'services_app/my_listings.html', {'listings': listings})
