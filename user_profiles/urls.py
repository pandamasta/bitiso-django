from django.urls import path
from . import views

urlpatterns = [
    # UUID-based profile URL
    path('<uuid:uuid>/', views.ProfileView.as_view(), name='profile_view'), 
    # Username-based profile URL
    path('<str:username>/', views.ProfileView.as_view(), name='profile_view'),  
    path('edit/', views.ProfileEditView.as_view(), name='profile_edit'),
]
