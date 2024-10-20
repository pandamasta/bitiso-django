# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import verify_email
from django.conf import settings

if settings.USE_UUID_FOR_PROFILE_URL:
    profile_url_pattern = path('profile/<uuid:uuid>/', views.profile_view, name='profile_view')
else:
    profile_url_pattern = path('profile/<str:username>/', views.profile_view, name='profile_view')

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('verify/<uidb64>/<token>/', verify_email, name='verify_email'),
    # path('profile/', views.profile, name='profile'),
    profile_url_pattern,  # Profile view based on UUID or Username

]

urlpatterns += [
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

