#  core/user_profiles/urls.py
from django.urls import path
from . import views
from django.conf import settings
from .views import user_dashboard

urlpatterns = [
    # UUID-based profile URL
    path('<uuid:uuid>/', views.ProfileView.as_view(), name='profile_view'),  
    # Username-based profile URL
    path('<str:username>/', views.ProfileView.as_view(), name='profile_view'),  
    path('dashboard/', user_dashboard, name='dashboard'),

]

# Conditionally add profile edit URL based on settings
if settings.USE_UUID_FOR_PROFILE_URL:
    urlpatterns += [
        path('<uuid:uuid>/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    ]
else:
    urlpatterns += [
        path('<str:username>/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    ]
