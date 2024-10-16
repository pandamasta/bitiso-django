# pages/views.py

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from .models import Page
from django.views.generic import TemplateView

# class HomePageView(TemplateView):
#     """Displays the homepage."""
#     template_name = 'pages/home.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Optionally, add extra context if needed
#         context['latest_pages'] = Page.objects.filter(is_published=True).order_by('-created_at')[:5]
#         return context
    
# from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'pages/home.html'


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
