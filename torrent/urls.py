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

app_name = 'bitiso'


urlpatterns = [
    # Public routes (available to everyone)
    path('', HomePageView.as_view(), name='torrent_homepage'),  # Home page
    path('torrents/', TorrentListView.as_view(), name='torrent_list'),  # List all torrents
    path('torrents/search/', search_view, name='torrent_search'),  # Search torrents
    path('torrents/<slug>/', TorrentDetailView.as_view(), name='torrent_detail'),  # Torrent detail view
    path('projects/', ProjectListView.as_view(), name='project_list'),  # List all projects
    path('projects/<slug:project_slug>/', ProjectDetailBySlugView.as_view(), name='project_detail_by_slug'),

    # Static pages
    path('about/', TemplateView.as_view(template_name="bt/about.html"), name='static_about'),  # About page
    path('faq/', TemplateView.as_view(template_name="bt/faq.html"), name='static_faq'),  # FAQ page
    path('contact/', TemplateView.as_view(template_name="bt/contact.html"), name='static_contact'),  # Contact page

    # Torrent management routes (authenticated)
    path('manage/torrents/create/', TorrentCreateView.as_view(), name='manage_torrent_create'),  # Create a new torrent
    path('manage/torrents/<slug:slug>/edit/', TorrentUpdateView.as_view(), name='manage_torrent_edit'),  # Edit an existing torrent
    path('manage/torrents/<slug:slug>/delete/', TorrentDeleteView.as_view(), name='manage_torrent_delete'),  # Delete a torrent
    path('manage/torrents/upload/', file_upload, name='manage_torrent_upload'),  # Upload a torrent file
    path('manage/torrents/download/', download_torrent, name='manage_torrent_download'),  # Download a torrent file
    path('manage/torrents/delete/', delete_torrents, name='manage_torrent_bulk_delete'),  # Bulk delete torrents

    # Project management routes (authenticated)
    path('manage/projects/create/', ProjectCreateView.as_view(), name='manage_project_create'),  # Create a new project
    path('manage/projects/<slug:slug>/edit/', ProjectUpdateView.as_view(), name='manage_project_edit'),  # Edit an existing project
    path('manage/projects/<slug:slug>/delete/', ProjectDeleteView.as_view(), name='manage_project_delete'),  # Delete a project

    # Management dashboard
    path('manage/', dashboard, name='manage_dashboard'),  # Management dashboard

    # Authentication routes
    path('login/', login_view, name='auth_login'),  # User login
    path('logout/', logout_view, name='auth_logout'),  # User logout
    path('register/', register_view, name='auth_register'),  # User registration
]