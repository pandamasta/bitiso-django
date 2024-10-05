from django.urls import path, include
from django.views.generic import TemplateView
from .views import (
    TorrentListView,
    TorrentDetailView,
    TorrentCreateView,
    TorrentUpdateView,
    TorrentDeleteView,
    file_upload,
    download_torrent,
    search_view,
    login_view,
    register_view,
    logout_view,
    dashboard,
    delete_torrents
)

# Public routes (available to everyone)
public_patterns = [
    path('', TorrentListView.as_view(), name='torrent_list'),  # Root for torrents
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    # path('torrent/<slug:slug>/', TorrentDetailView.as_view(), name='torrent_detail'),
    path('torrents/search/', search_view, name='torrent_search'),  # Search
    path('torrent/<slug>/', TorrentDetailView.as_view(), name='torrent_detail'),


    # Static Pages
    path('about/', TemplateView.as_view(template_name="bt/about.html"), name="about"),
    path('faq/', TemplateView.as_view(template_name="bt/faq.html"), name="faq"),
    path('contact/', TemplateView.as_view(template_name="bt/contact.html"), name="contact"),
]

# Management routes (authenticated users)
manage_patterns = [
    path('create/', TorrentCreateView.as_view(), name='torrent_create'),
    path('<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_edit'),
    path('<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),
    path('upload/', file_upload, name='torrent_upload'),
    path('download/', download_torrent, name='torrent_download'),
    path('delete/', delete_torrents, name='torrent_bulk_delete'),
    path('', dashboard, name='torrent_dashboard'),  # Dashboard for managing torrents
]

# Combine the public, management, and other routes
urlpatterns = [
    # Public routes
    path('', include(public_patterns)),

    # Management routes (all under /torrent/manage/)
    path('torrent/manage/', include((manage_patterns, 'torrent_manage'))),
]
# urlpatterns = [

#     # path('', views.torrent_list_view, name='torrent_list'),
#     # # path('', search, name='torrent/index.html'),
#     # path('search/', views.search_view, name='torrent_search'),
#     # path('detail/<torrent_name>/', views.detail),
#     # path('category/<category_id>/', views.category),
#     # path('project/', views.project, name='project_detail'),
#     # path('project/<str:identifier>/', views.project_detail, name='project_detail'),
#     path('', TorrentListView.as_view(), name='torrent_list'),  # <-- Add this line
#     # path('torrents/', include('torrent.urls')),  # This will still handle any other torrent routes
#     # User Authentication
#     path('login/', login_view, name='login'),
#     path('logout/', logout_view, name='logout'),
#     path('register/', register_view, name='register'),

#     # Dashboard
#     path('dashboard/', dashboard, name='dashboard') ,

#     # Torrents

#     # Public routes
#     path('', TorrentListView.as_view(), name='torrent_list'),  # Root for torrents
#     path('<slug:slug>/', TorrentDetailView.as_view(), name='torrent_detail'),  # Detail view
#     path('torrents/search/', search_view, name='torrent_search'),

#     # Manage Torrents (User authenticated actions)
#     path('torrent/manage/', dashboard, name='torrent_manage'), 
#     path('torrent/manage/create/', TorrentCreateView.as_view(), name='torrent_create'),  # Create a torrent
#     path('torrent/manage/<slug:slug>/edit/', TorrentUpdateView.as_view(), name='torrent_edit'),  # Edit a torrent
#     path('torrent/manage/<slug:slug>/delete/', TorrentDeleteView.as_view(), name='torrent_delete'),  # Delete a torrent
#     path('torrent/manage/upload/', file_upload, name='torrent_upload'), # Upload .torrent and import to DB
#     path('torrent/manage/download/', download_torrent, name='torrent_download'), # Download from URL
#     path('torrent/manage/delete/', delete_torrents, name='torrent_bulk_delete'), # bulk delete

#     #path('torrent/manage/files/upload/', file_upload, name='torrent_file_upload'),
#     #path('torrent/manage/files/download/', download_torrent, name='torrent_file_download'),

#     ################

#     # Categories
#     path('categories/', CategoryListView.as_view(), name='category_list'),
#     path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),

#     # Projects
#     path('projects/', ProjectListView.as_view(), name='project_list'),
#     path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
#     path('projects/<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
#     path('projects/<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_update'),
#     path('projects/<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

#     # Static Pages
#     path('about/', TemplateView.as_view(template_name="torrent/about.html"), name="about"),
#     path('faq/', TemplateView.as_view(template_name="torrent/faq.html"), name="faq"),
#     path('contact/', TemplateView.as_view(template_name="torrent/contact.html"), name="contact"),

#     # Admin actions for managing categories and projects
#     # path('admin/categories/', CategoryListView.as_view(), name='category_admin_list'),
#     # path('admin/categories/create/', CategoryCreateView.as_view(), name='category_admin_create'),
#     # path('admin/categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_admin_edit'),
#     # path('admin/projects/', ProjectListView.as_view(), name='project_admin_list'),
#     # path('admin/projects/create/', ProjectCreateView.as_view(), name='project_admin_create'),
#     # path('admin/projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_admin_edit'),
# ]
