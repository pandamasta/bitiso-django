# pages/urls.py
from django.urls import path
from .views import PageDetailView, HomePageView

urlpatterns = [
    #path('', HomePageView.as_view(), name='home'),  # Home page
    # path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),  # Dynamic page view by slug
    path('', PageDetailView.as_view(), name='page_detail'),  # Match slug to page details

]
