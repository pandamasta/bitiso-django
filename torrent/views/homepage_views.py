from django.views.generic import ListView
from ..models import Torrent
from ..mixins import RateLimitMixin
from ..forms import SearchForm


def get_top_seeded_torrents():
    return Torrent.objects.filter(is_active=True).order_by('-seed')[:10]  # Query for top seeded torrents


class HomePageView(ListView):
    model = Torrent
    template_name = 'bt/homepage.html'
    context_object_name = 'torrent_list'
    paginate_by = 40  # Adjust as needed

    def get_queryset(self):
        torrents = Torrent.objects.filter(is_active=True).order_by('-creation')
        query = self.request.GET.get('query')

        # If there's a search query, filter by name
        if query:
            torrents = torrents.filter(name__icontains=query)

        return torrents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()  # Add the search form to the context
        context['top_seeded_torrent_list'] = get_top_seeded_torrents()  # Add top seeded torrents to the context
        return context

    def get_form(self):
        return SearchForm(self.request.GET or None)  # Create or populate the search form

