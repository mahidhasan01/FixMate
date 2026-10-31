from django.urls import path

from . import views

app_name = 'services_app'

urlpatterns = [
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/mine/', views.my_listings, name='my_listings'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('workers/<int:pk>/', views.worker_profile, name='worker_profile'),
    path('listings/new/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/update/', views.listing_update, name='listing_update'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
]
