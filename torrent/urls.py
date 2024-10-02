from django.urls import path
from django.views.generic import TemplateView
from .views import (
    TorrentListView,
    TorrentDetailView,
    TorrentCreateView,
    TorrentUpdateView,
    TorrentDeleteView,
    CategoryListView,
    CategoryDetailView,
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    login_view,
    logout_view,
    register_view,
    dashboard,
    file_upload,
    download_torrent,
    search_view,
    manage_torrents,
    delete_torrents,
)

urlpatterns = [
    # User Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # Torrents
    path('torrents/', TorrentListView.as_view(), name='torrent_list'),
    path('torrents/create/', TorrentCreateView.as_view(), name='torrent_create'),
    path('torrents/<slug:slug>/', TorrentDetailView.as_view(), name='torrent_detail'),
    path('torrents/<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_update'),
    path('torrents/<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),
    path('torrents/upload/', file_upload, name='file_upload'),
    path('torrents/download/', download_torrent, name='download_torrent'),
    path('torrents/search/', search_view, name='torrent_search'),
    path('torrents/manage/', manage_torrents, name='manage_torrents'),
    path('torrents/delete/', delete_torrents, name='delete_torrents'),

    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),

    # Projects
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    # Static Pages
    path('about/', TemplateView.as_view(template_name="torrent/about.html"), name="about"),
    path('faq/', TemplateView.as_view(template_name="torrent/faq.html"), name="faq"),
    path('contact/', TemplateView.as_view(template_name="torrent/contact.html"), name="contact"),
]
