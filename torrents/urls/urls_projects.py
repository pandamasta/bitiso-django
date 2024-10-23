from django.urls import path
from torrents import views
from django.conf import settings

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('<slug:slug>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
]