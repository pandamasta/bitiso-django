# from django.urls import path
# #from . import views
# from torrents import views
# from .views import upload_local_torrent, import_torrent_from_url

# urlpatterns = [
#     # Torrent URLs
#     path('', views.TorrentListView.as_view(), name='torrent_list'),
#     path('<slug:slug>/', views.TorrentDetailView.as_view(), name='torrent_detail'),
#     path('<slug:slug>/create/', views.TorrentCreateView.as_view(), name='torrent_create'),
#     path('<slug:slug>/edit/', views.TorrentUpdateView.as_view(), name='torrent_edit'),
#     path('<slug:slug>/delete/', views.TorrentDeleteView.as_view(), name='torrent_delete'),

#     # Project URLs
#     path('projects/', views.ProjectListView.as_view(), name='project_list'),
#     path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
#     path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
#     path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
#     path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

#     # Category URLs
#     path('categories/', views.CategoryListView.as_view(), name='category_list'),
#     path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
#     path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
#     path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
#     path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

#     # Tracker URLs
#     path('trackers/', views.TrackerListView.as_view(), name='tracker_list'),
#     path('trackers/create/', views.TrackerCreateView.as_view(), name='tracker_create'),
#     path('trackers/<int:pk>/', views.TrackerDetailView.as_view(), name='tracker_detail'),
#     path('trackers/<int:pk>/edit/', views.TrackerUpdateView.as_view(), name='tracker_edit'),
#     path('trackers/<int:pk>/delete/', views.TrackerDeleteView.as_view(), name='tracker_delete'),

#     path('upload/', upload_local_torrent, name='upload_local_torrent'),
#     path('import-from-url/', import_torrent_from_url, name='import_torrent_from_url'),
# ]
