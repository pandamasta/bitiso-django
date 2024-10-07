from django.urls import path, include
from .views import (
    # Torrent Views
    TorrentListView, TorrentDetailView, TorrentCreateView,
    TorrentUpdateView, TorrentDeleteView,

    # Project Views
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView, ProjectDetailByIdView, ProjectDetailBySlugView,

    # Auth Views
    login_view, logout_view, register_view,

    # Other Views
    search_view, dashboard, file_upload, download_torrent, delete_torrents
)
from django.views.generic import TemplateView

# Public routes (available to everyone)

public_patterns = [
    # Torrent-related public views
    path('', TorrentListView.as_view(), name='torrent_list'),  # Root for torrents
    path('torrent/', TorrentListView.as_view(), name='torrent_list'),  # Root for torrents

    path('torrents/<slug>/', TorrentDetailView.as_view(), name='torrent_detail'),  # Detail view
    path('torrents/search/', search_view, name='torrent_search'),  # Search

    # Project-related public views
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List of projects
    path('projects/<int:id>/', ProjectDetailByIdView.as_view(), name='project_detail_by_id'),
    path('projects/<slug:slug>/', ProjectDetailBySlugView.as_view(), name='project_detail_by_slug'),

    # Static Pages
    path('about/', TemplateView.as_view(template_name="bt/about.html"), name="about"),
    path('faq/', TemplateView.as_view(template_name="bt/faq.html"), name="faq"),
    path('contact/', TemplateView.as_view(template_name="bt/contact.html"), name="contact"),
]

# Torrent management (authenticated actions)
torrent_manage_patterns = [
    path('create/', TorrentCreateView.as_view(), name='torrent_create'),  # Create a torrent
    path('<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_edit'),  # Edit a torrent
    path('<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),  # Delete a torrent
    path('upload/', file_upload, name='torrent_upload'),  # Upload a torrent
    path('download/', download_torrent, name='torrent_download'),  # Download a torrent
    path('delete/', delete_torrents, name='torrent_bulk_delete'),  # Bulk delete torrents
]

# Project management (authenticated actions)
project_manage_patterns = [
    path('create/', ProjectCreateView.as_view(), name='project_create'),  # Create a project
    path('<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_edit'),  # Edit a project
    path('<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),  # Delete a project
]

# Combined manage patterns (for dashboard and torrent/project management)
manage_patterns = [
    path('torrents/', include((torrent_manage_patterns, 'torrent'), namespace='torrent_manage')),  # Torrent manage
    path('projects/', include((project_manage_patterns, 'project'), namespace='project_manage')),  # Project manage
    path('', dashboard, name='dashboard'),  # Dashboard for managing
]

# Auth routes (login, logout, register)
auth_patterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # Logout should be under auth
    path('register/', register_view, name='register'),
]

# Main URL patterns
urlpatterns = [
    # Public routes
    path('', include(public_patterns)),

    # Management routes (all under /manage/)
    path('manage/', include((manage_patterns, 'manage'), namespace='manage')),

    # Authentication routes
    path('', include(auth_patterns)),
]

