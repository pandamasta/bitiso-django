from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from pages.views import HomePageView, redirect_to_language_home

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching
    path('', redirect_to_language_home, name='redirect_home'),  # Redirect root URL to the language-specific homepage
]

# i18n URL patterns (language-prefixed routes like /fr/, /en/)
urlpatterns += i18n_patterns(
    path('', HomePageView.as_view(), name='home'),  # Root URL for the homepage
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('pages/', include('pages.urls')),  # Pages URLs under /pages/
)
