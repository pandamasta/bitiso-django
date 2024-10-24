#torrents/urls/urls_torrents.py

from django.urls import path
from torrents import views
from django.conf import settings
#from ..views import upload_local_torrent, import_torrent_from_url

# Set URL patterns based on the USE_SLUG_IN_URLS setting

from ..views.torrents_views import (
    TorrentListView, TorrentDetailView, TorrentCreateView,
    TorrentUpdateView, TorrentDeleteView
)

from torrents.views import upload_local_torrent, import_torrent_from_url

urlpatterns = [
    # Torrent URLs
    # path('upload/', upload_local_torrent, name='upload_local_torrent'),
    # path('import-from-url/', import_torrent_from_url, name='import_torrent_from_url'),

    path('upload/', upload_local_torrent, name='torrent_upload'),  # Correct name
    path('import-from-url/', import_torrent_from_url, name='torrent_import_from_url'),
    path('', TorrentListView.as_view(), name='torrent_list'),
    path('<slug:slug>/', TorrentDetailView.as_view(), name='torrent_detail'),
    path('<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_edit'),
    path('<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),

]


