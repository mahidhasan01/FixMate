from django.urls import path

from . import views

app_name = 'payment_app'

urlpatterns = [
    path('checkout/<int:booking_pk>/', views.checkout, name='checkout'),
]
