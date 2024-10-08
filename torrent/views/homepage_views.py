from django.views.generic import ListView
from ..models import Torrent
from ..mixins import RateLimitMixin
from ..forms import SearchForm

class HomePageView(RateLimitMixin, ListView):
    model = Torrent
    template_name = 'bt/homepage.html'
    context_object_name = 'torrent_list'
    paginate_by = 40  # Adjust as needed

    # RateLimit settings for the homepage
    rate_limit_key = 'homepage'
    limit = 20  # requests per minute
    period = 60  # time period in seconds

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
        context['top_seeded_torrent_list'] = self.get_top_seeded_torrents()  # Add top seeded torrents to the context
        return context

    def get_form(self):
        return SearchForm(self.request.GET or None)  # Create or populate the search form

    def get_top_seeded_torrents(self):
        return Torrent.objects.filter(is_active=True).order_by('-seed')[:10]  # Query for top seeded torrents