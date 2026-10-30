from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'accounts_app'

urlpatterns = [
    path('signup/', views.choose_role, name='choose_role'),
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('signup/worker/', views.worker_signup, name='worker_signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts_app/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('after_login/', views.after_login, name='after_login'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/id_verification/', views.id_verification, name='id_verification'),
    path('profile/worker_verification/', views.worker_verification, name='worker_verification'),
    path('staff/verification_queue/', views.verification_queue, name='verification_queue'),
    path('staff/customer_id/<int:pk>/review/', views.review_customer_id, name='review_customer_id'),
    path('staff/worker_verification/<int:pk>/review/', views.review_worker_verification,
         name='review_worker_verification'),
    path('private/customer_id/<int:pk>/', views.customer_id_photo, name='customer_id_photo'),
    path('private/worker_document/<int:pk>/', views.worker_document, name='worker_document'),
]
