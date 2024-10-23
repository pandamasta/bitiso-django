from django.urls import path
from torrents import views
from django.conf import settings

# Set URL patterns based on the USE_SLUG_IN_URLS setting

urlpatterns = [
    path('', views.TrackerListView.as_view(), name='tracker_list'),
    path('create/', views.TrackerCreateView.as_view(), name='tracker_create'),
    path('<slug:slug>', views.TrackerDetailView.as_view(), name='tracker_detail'),
    path('<slug:slug>edit/', views.TrackerUpdateView.as_view(), name='tracker_edit'),
    path('<slug:slug>/delete/', views.TrackerDeleteView.as_view(), name='tracker_delete'),
]
