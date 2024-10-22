from django.urls import path
from . import views

# torrents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.TorrentListView.as_view(), name='torrent_list'),  # List view for torrents
    path('create/', views.TorrentCreateView.as_view(), name='torrent_create'),
    path('<slug:slug>/', views.TorrentDetailView.as_view(), name='torrent_detail'),
    path('<slug:slug>/edit/', views.TorrentUpdateView.as_view(), name='torrent_edit'),
    path('<slug:slug>/delete/', views.TorrentDeleteView.as_view(), name='torrent_delete'),
]
