#torrents/urls/categories.py
from django.urls import path
from torrents import views
from django.conf import settings

from ..views.categories import (
    CategoryListView,CategoryDetailView, CategoryCreateView,
    CategoryUpdateView, CategoryDeleteView
)

# Set URL patterns based on the USE_SLUG_IN_URLS setting

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),
    path('create/', CategoryCreateView.as_view(), name='category_create'),
    path('<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:slug>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
]
