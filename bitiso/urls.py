from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from core.pages.views import HomePageView, PageDetailView, redirect_to_language_home

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
    path('', redirect_to_language_home),  # Redirect root URL to language-specific home page
]

# i18n URL patterns for language-prefixed routes (like /fr/, /en/)
urlpatterns += i18n_patterns(
    path('', HomePageView.as_view(), name='home'),  # Home page URL should be named 'home'
    path('admin/', admin.site.urls),  # Admin paths
    path('accounts/', include('accounts.urls')),  # Accounts app paths
    path('profiles/', include('core.user_profiles.urls')),  # Include user_profiles URLs

    # Map slugs directly at the root for pages like /en/about/
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
)

