from django.urls import path
from torrents import views
from django.conf import settings
from ..views.actions import bulk_project_action

from ..views.projects import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView
)

urlpatterns = [
    # Add the bulk project action URL
    path('bulk-action/', bulk_project_action, name='bulk_project_action'),

    path('', ProjectListView.as_view(), name='project_list'),
    path('create/', ProjectCreateView.as_view(), name='project_create'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),


]