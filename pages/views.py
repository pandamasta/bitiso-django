# pages/views.py

from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView
from .models import Page
from django.utils import translation

def redirect_to_language_home(request):
    user_language = translation.get_language()
    return redirect(f'/{user_language}/')

class HomePageView(DetailView):
    template_name = 'pages/home.html'  # Use a dynamic home template
    context_object_name = 'page'

    def get_object(self):
        # Fetch the page marked as the homepage
        return get_object_or_404(Page, is_published=True, is_homepage=True)

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
