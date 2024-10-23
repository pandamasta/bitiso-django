
from django.urls import path
from torrents import views
from django.conf import settings

# Set URL patterns based on the USE_SLUG_IN_URLS setting

urlpatterns = [
    # Torrent URLs
    path('', views.TorrentListView.as_view(), name='torrent_list'),
    path('<slug:slug>/', views.TorrentDetailView.as_view(), name='torrent_detail'),
    path('<slug:slug>/edit/', views.TorrentUpdateView.as_view(), name='torrent_edit'),
    path('<slug:slug>/delete/', views.TorrentDeleteView.as_view(), name='torrent_delete'),
]

