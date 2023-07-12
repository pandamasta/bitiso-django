from django.urls import path, include

from . import views
#from rest_framework import routers
from django.urls import path
from django.views.generic import TemplateView

#router = routers.DefaultRouter()
#router.register(r'torrent', views.TorrentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #path('api', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('', views.index),
    path('detail/<info_hash>/', views.detail),
    path('category/<category_id>/', views.category),
    path('about/', TemplateView.as_view(template_name="torrent/about.html")),    
    path('faq/', TemplateView.as_view(template_name="torrent/faq.html")),    
    path('contact/', TemplateView.as_view(template_name="torrent/contact.html")),
]
