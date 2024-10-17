# pages/views.py

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from .models import Page
from django.views.generic import TemplateView

from django.views.generic import ListView, DetailView
from .models import Page

class HomePageView(ListView):
    template_name = 'home.html'
    context_object_name = 'page_list'

    def get_queryset(self):
        return Page.objects.filter(is_published=True)

class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'

    def get_object(self):
        return get_object_or_404(Page, slug=self.kwargs['slug'], is_published=True)


class PageListView(ListView):
    """Displays a list of all published pages."""
    model = Page
    template_name = 'pages/page_list.html'
    context_object_name = 'pages'

    def get_queryset(self):
        """Return only published pages."""
        return Page.objects.filter(is_published=True)
