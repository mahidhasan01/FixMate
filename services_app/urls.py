from django.urls import path

from . import views

app_name = 'services_app'

urlpatterns = [
    path('listings/mine/', views.my_listings, name='my_listings'),
]
