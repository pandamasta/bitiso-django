# bitiso/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # i18n URLs for language switching
    path('i18n/', include('django.conf.urls.i18n')),  # This enables the set_language view
]

# i18n URL patterns with language prefix (like /fr/, /en/)
urlpatterns += i18n_patterns(
    # Home page
    path('', views.home, name='home'),

    # Admin site
    path('admin/', admin.site.urls),

    # Accounts app URLs
    path('accounts/', include('accounts.urls')),
)
