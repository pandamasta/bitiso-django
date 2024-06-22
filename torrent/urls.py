from django.urls import path, include
from . import views
from django.urls import path
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = [
    path('', views.torrent_list_view),
    # path('', search, name='torrent/index.html'),
    path('detail/<torrent_name>/', views.detail),
    path('category/<category_id>/', views.category),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/', views.project, name='project_detail'),

    path('about/', TemplateView.as_view(template_name="torrent/about.html")),
    path('faq/', TemplateView.as_view(template_name="torrent/faq.html")),
    path('contact/', TemplateView.as_view(template_name="torrent/contact.html")),
    path('categories/', views.category_list, name='category_list'),

    path('manage/', views.manage_torrents, name='manage_torrents'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/torrent/', views.dashboard, name='dashboard_torrent'),
    path('dashboard/project/', views.dashboard_project, name='dashboard_project'),
    path('dashboard/project/<int:project_id>/torrents/', views.list_torrents, name='list_torrents'),

    path('delete_torrents/', views.delete_torrents, name='delete_torrents'),
    path('upload/', views.file_upload, name='file_upload'),
    path('download_torrent/', views.download_torrent, name='download_torrent'),

]
admin.site.index_template = 'admin/index.html'
admin.autodiscover()
