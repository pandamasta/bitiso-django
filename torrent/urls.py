from django.urls import path, include
from . import views
from django.urls import path
from django.views.generic import TemplateView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.index),
    path('detail/<info_hash>/', views.detail),
    path('category/<category_id>/', views.category),
    path('project/<int:project_id>/', views.project_detail, name='torrent/project_detail.html'),
    path('project/', views.project),

    path('about/', TemplateView.as_view(template_name="torrent/about.html")),    
    path('faq/', TemplateView.as_view(template_name="torrent/faq.html")),    
    path('contact/', TemplateView.as_view(template_name="torrent/contact.html")),
]
