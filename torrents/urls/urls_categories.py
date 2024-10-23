from django.urls import path
from torrents import views
from django.conf import settings

# Set URL patterns based on the USE_SLUG_IN_URLS setting

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
