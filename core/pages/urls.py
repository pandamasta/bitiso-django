# pages/urls.py
from django.urls import path
from .views import PageDetailView, PageUpdateView

urlpatterns = [
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),  # Dynamic page view by slug
    path('<slug:slug>/edit/', PageUpdateView.as_view(), name='page_edit'),  # Ensure name matches here too
]