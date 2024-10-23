# bitiso/urls.py

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from core.pages.views import HomePageView, PageDetailView, PageUpdateView, redirect_to_language_home
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
    path('', redirect_to_language_home),  # Redirect root URL to language-specific home page
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# i18n URL patterns for language-prefixed routes (like /fr/, /en/)
urlpatterns += i18n_patterns(
    path('', HomePageView.as_view(), name='home'),  # Home page URL should be named 'home'
    path('admin/', admin.site.urls),  # Admin paths
    path('accounts/', include('core.accounts.urls')),  # Accounts app paths
    path('profiles/', include('core.user_profiles.urls')),  # Include user_profiles URLs

    # Project, category, and tracker routes
    path('torrents/', include('torrents.urls.urls_torrents')),  # Torrents app URLs
    path('projects/', include('torrents.urls.urls_projects')),  # Project URLs
    path('categories/', include('torrents.urls.urls_categories')),  # Category URLs
    path('trackers/', include('torrents.urls.urls_trackers')),  # Tracker URLs
        
    # Pages URL patterns
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
    path('<slug:slug>/edit/', PageUpdateView.as_view(), name='page_edit'),  # Ensure consistency here

)

