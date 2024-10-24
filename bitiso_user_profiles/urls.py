# bitiso/bitiso_user_profiles.py

from django.urls import path
from .views import BitisoUserProfileEditView, BitisoUserProfileView  # Import the correct views

urlpatterns = [
    # Profile View and Edit for UUID-based or username-based URLs
    path('<uuid:uuid>/', BitisoUserProfileView.as_view(), name='profile_view'),
    path('<uuid:uuid>/edit/', BitisoUserProfileEditView.as_view(), name='profile_edit'),
    
    # Optionally, if you also support username-based URLs
    path('<str:username>/', BitisoUserProfileView.as_view(), name='profile_view'),
    path('<str:username>/edit/', BitisoUserProfileEditView.as_view(), name='profile_edit'),
]
