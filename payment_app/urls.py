from django.urls import path

from . import views

app_name = 'payment_app'

urlpatterns = [
    path('checkout/<int:booking_pk>/', views.checkout, name='checkout'),
    path('staff/queue/', views.payment_queue, name='payment_queue'),
    path('<int:pk>/review/', views.payment_review, name='payment_review'),
    path('<int:pk>/cash_received/', views.cash_received, name='cash_received'),
    path('<int:pk>/receipt/', views.receipt, name='receipt'),
    path('history/', views.payment_history, name='payment_history'),
]
