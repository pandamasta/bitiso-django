# urls.py

from django.urls import path, include
from django.views.generic import TemplateView
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

# Public URL patterns for anyone to access
public_patterns = [
    # Homepage
    path('', HomePageView.as_view(), name='homepage'),  # Home page

    # Torrent-related views (public)
    path('torrents/', TorrentListView.as_view(), name='torrent_list'),  # List all torrents
    path('torrents/search/', search_view, name='torrent_search'),  # Search torrents
    path('torrents/<slug>/', TorrentDetailView.as_view(), name='torrent_detail'),  # Torrent detail view

    # Project-related views (public)
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List of all projects
    path('projects/<slug:project_slug>/', ProjectDetailBySlugView.as_view(), name='project_detail_by_slug'),  # Project detail by slug

    # Static pages
    path('about/', TemplateView.as_view(template_name="bt/about.html"), name="about"),  # About page
    path('faq/', TemplateView.as_view(template_name="bt/faq.html"), name='faq'),  # FAQ page
    path('contact/', TemplateView.as_view(template_name="bt/contact.html"), name='contact'),  # Contact page
]

# Torrent management URLs (requires authentication)
torrent_manage_patterns = [
    path('create/', TorrentCreateView.as_view(), name='torrent_create'),  # Create a new torrent
    path('<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_edit'),  # Edit an existing torrent
    path('<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),  # Delete a torrent
    path('upload/', file_upload, name='torrent_upload'),  # Upload a torrent file
    path('download/', download_torrent, name='torrent_download'),  # Download a torrent file
    path('delete/', delete_torrents, name='torrent_bulk_delete'),  # Bulk delete torrents
]

# Project management URLs (requires authentication)
project_manage_patterns = [
    path('create/', ProjectCreateView.as_view(), name='project_create'),  # Create a new project
    path('<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_edit'),  # Edit an existing project
    path('<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),  # Delete a project
]

# Dashboard and management section (requires authentication)
manage_patterns = [
    path('', dashboard, name='dashboard'),  # Management dashboard
    path('torrents/', include((torrent_manage_patterns, 'torrent_manage'))),  # Manage torrents
    path('projects/', include((project_manage_patterns, 'project_manage'))),  # Manage projects
]

# Authentication-related routes (login, logout, registration)
auth_patterns = [
    path('login/', login_view, name='login'),  # User login
    path('logout/', logout_view, name='logout'),  # User logout
    path('register/', register_view, name='register'),  # User registration
]

# Main URL patterns for the project
urlpatterns = [
    path('', include(public_patterns)),  # Public URLs
    path('manage/', include((manage_patterns, 'manage'))),  # Management URLs under /manage/
    path('', include(auth_patterns)),  # Authentication URLs
]
