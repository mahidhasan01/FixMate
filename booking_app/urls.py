from django.urls import path

from . import views

app_name = 'booking_app'

urlpatterns = [
    path('mine/', views.customer_bookings, name='customer_bookings'),
    path('requests/', views.worker_bookings, name='worker_bookings'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/respond/', views.booking_respond, name='booking_respond'),
    path('new/<int:listing_pk>/', views.booking_create, name='booking_create'),
]
