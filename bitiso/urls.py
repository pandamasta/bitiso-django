# bitiso/urls.py

import os
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from core.pages.views import HomePageView, PageDetailView, PageUpdateView, redirect_to_language_home
from django.conf.urls.static import static
from django.conf import settings
from torrents.views.torrents import serve_torrent_file


from dotenv import load_dotenv  # python-dotenv
load_dotenv()  # Loads variables from the .env file


# Get the accounts path from the environment variable, with a default fallback
accounts_path = os.getenv('ACCOUNTS_PATH', 'accounts/')
admin_path = os.getenv('ADMIN_PATH', 'admin/')


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
    path('', redirect_to_language_home),  # Redirect root URL to language-specific home page
    
    # Add serve_torrent_file outside i18n_patterns to avoid language prefix
    path('t/<path:filename>', serve_torrent_file, name='serve_torrent_file'),
] 

# Serving static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# i18n URL patterns for language-prefixed routes (like /fr/, /en/)
urlpatterns += i18n_patterns(
    path('', HomePageView.as_view(), name='home'),  # Home page URL should be named 'home'
    path(admin_path, admin.site.urls),  # Use the variable for the admin path
    path(accounts_path, include('core.accounts.urls')),  # Accounts app paths

    path('profiles/', include('bitiso_user_profiles.urls')),  # Ensure you include the bitiso_user_profiles URLs

    # Project, category, and tracker routes
    path('torrents/', include('torrents.urls.torrents')),  # Torrents app URLs
    path('projects/', include('torrents.urls.projects')),  # Project URLs
    path('categories/', include('torrents.urls.categories')),  # Category URLs
    path('trackers/', include('torrents.urls.trackers')),  # Tracker URLs
    
    # Pages URL patterns
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
    path('<slug:slug>/edit/', PageUpdateView.as_view(), name='page_edit'),  # Ensure consistency here

)

