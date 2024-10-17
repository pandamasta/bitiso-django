# bitiso/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from pages.views import HomePageView

from django.contrib import admin
from django.urls import path, include
from pages.views import HomePageView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', HomePageView.as_view(), name='home'),  # Homepage
    path('<slug:slug>/', include('pages.urls')),    # Pages app
]


# # i18n URL patterns for language-prefixed routes (like /fr/, /en/)
urlpatterns += i18n_patterns(
path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),  # Includes the dynamic pages app URLs
)
