from django.urls import path
from torrents import views
from django.conf import settings

from ..views.projects import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView
)

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('create/', ProjectCreateView.as_view(), name='project_create'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
]