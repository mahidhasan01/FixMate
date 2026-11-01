from django.urls import path

from . import views

app_name = 'booking_app'

urlpatterns = [
    path('mine/', views.customer_bookings, name='customer_bookings'),
    path('requests/', views.worker_bookings, name='worker_bookings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/flags/', views.flag_list, name='flag_list'),
    path('staff/flags/<int:pk>/update/', views.flag_update, name='flag_update'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/respond/', views.booking_respond, name='booking_respond'),
    path('<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<int:pk>/completion/', views.completion_upload, name='completion_upload'),
    path('<int:pk>/completion/review/', views.completion_review, name='completion_review'),
    path('<int:pk>/review/new/', views.review_create, name='review_create'),
    path('reviews/<int:pk>/update/', views.review_update, name='review_update'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('new/<int:listing_pk>/', views.booking_create, name='booking_create'),
]
