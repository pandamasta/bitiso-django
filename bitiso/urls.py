from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from core.pages.views import HomePageView, PageDetailView, redirect_to_language_home
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
    # Specific paths for projects, categories, and trackers inside torrents app
    path('torrents/', include('torrents.urls.urls_torrents')),  # Include the torrents app URLs
    path('projects/', include('torrents.urls.urls_projects')),  # Separate URLs for projects
    path('categories/', include('torrents.urls.urls_categories')),  # Separate URLs for categories
    path('trackers/', include('torrents.urls.urls_trackers')),  # Separate URLs for trackers
    
    
    # Map slugs directly at the root for pages like /en/about/
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),

)

