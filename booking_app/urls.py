from django.urls import path

from . import views

app_name = 'booking_app'

urlpatterns = [
    path('mine/', views.customer_bookings, name='customer_bookings'),
]
