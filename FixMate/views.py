from django.shortcuts import render

from accounts_app.models import WorkerProfile
from services_app.models import ServiceCategory, ServiceListing


def home(request):
    context = {
        'categories': ServiceCategory.objects.order_by('name'),
        'top_workers': WorkerProfile.objects.filter(verified_badge=True).order_by('-average_rating')[:4],
        'latest_listings': ServiceListing.objects.order_by('-id')[:6],
    }
    return render(request, 'home.html', context)
