from django.urls import path
from torrents import views
from django.conf import settings

from ..views.trackers_views import (
    TrackerListView,TrackerDetailView, TrackerCreateView,
    TrackerUpdateView, TrackerDeleteView
)
urlpatterns = [
    path('', TrackerListView.as_view(), name='tracker_list'),
    path('create/', TrackerCreateView.as_view(), name='tracker_create'),
    path('<slug:slug>', TrackerDetailView.as_view(), name='tracker_detail'),
    path('<slug:slug>edit/', TrackerUpdateView.as_view(), name='tracker_edit'),
    path('<slug:slug>/delete/', TrackerDeleteView.as_view(), name='tracker_delete'),
]
