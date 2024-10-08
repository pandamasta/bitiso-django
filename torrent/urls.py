from django.urls import path, include
from .views import (
    # Homepage
    HomePageView,

    # Torrent views
    TorrentListView, TorrentDetailView, TorrentCreateView, TorrentUpdateView, TorrentDeleteView,
    file_upload, download_torrent, delete_torrents, search_view,

    # Project views
    ProjectListView, ProjectDetailBySlugView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,

    # Auth views
    login_view, logout_view, register_view,

    # Dashboard
    dashboard
)

from django.views.generic import TemplateView

# Public routes (available to everyone)
public_patterns = [
    # Torrent-related public views
    path('', HomePageView.as_view(), name='homepage'),  # Home page

    path('torrents/', TorrentListView.as_view(), name='torrent_list'),  # Redundant root for torrents
    path('torrents/search/', search_view, name='torrent_search'),  # Search torrents
    path('torrents/<slug>/', TorrentDetailView.as_view(), name='torrent_detail'),  # Torrent details

    # Project-related public views
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List of projects
    path('projects/<slug:project_slug>/', ProjectDetailBySlugView.as_view(), name='project_detail_by_slug'),  # Project detail view

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

# Management patterns (for dashboard and torrent/project management)
manage_patterns = [
    path('', dashboard, name='dashboard'),  # Dashboard for managing
    path('torrents/', include((torrent_manage_patterns, 'torrent_manage'))),  # Manage torrents
    path('projects/', include((project_manage_patterns, 'project_manage'))),  # Manage projects
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
    path('manage/', include((manage_patterns, 'manage'))),

    # Authentication routes
    path('', include(auth_patterns)),
]