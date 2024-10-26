# bitiso_user_profiles/urls.py

from django.urls import path
from .views import BitisoUserProfileEditView, BitisoUserProfileView  # Import the correct views
from .views import user_dashboard, user_torrents, user_projects, user_categories

urlpatterns = [

    path('dashboard/', user_dashboard, name='dashboard'),
    path('dashboard/torrents/', user_torrents, name='user_torrents'),
    path('dashboard/projects/', user_projects, name='user_projects'),
    path('dashboard/categories/', user_categories, name='user_categories'),


    # Profile View and Edit for UUID-based or username-based URLs
    path('<uuid:uuid>/', BitisoUserProfileView.as_view(), name='profile_view'),
    path('<uuid:uuid>/edit/', BitisoUserProfileEditView.as_view(), name='profile_edit'),
    
    # Optionally, if you also support username-based URLs
    path('<str:username>/', BitisoUserProfileView.as_view(), name='profile_view'),
    path('<str:username>/edit/', BitisoUserProfileEditView.as_view(), name='profile_edit'),


]
