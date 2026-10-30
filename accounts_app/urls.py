from django.urls import path

from . import views

app_name = 'accounts_app'

urlpatterns = [
    path('signup/', views.choose_role, name='choose_role'),
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('signup/worker/', views.worker_signup, name='worker_signup'),
]
