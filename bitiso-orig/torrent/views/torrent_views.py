# views/torrent_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Torrent

from ..forms import SearchForm


class TorrentListView(ListView):
    model = Torrent
    template_name = 'bt/torrent_list.html'
    context_object_name = 'torrent_list'
    paginate_by = 40  # Pagination setting

    def get_context_data(self, **kwargs):
        # Add search form to the context
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def get_queryset(self):
        # Query for active torrents, ordered by creation date
        torrents = Torrent.objects.filter(is_active=True).order_by('-creation')
        form = self.get_form()

        # Handle search query if form is valid
        if form.is_valid() and form.cleaned_data['query']:
            query = form.cleaned_data['query']
            torrents = torrents.filter(name__icontains=query)

        return torrents

    def get_form(self):
        # Get the search form, populate it with GET data if available
        return SearchForm(self.request.GET or None)


class TorrentDetailView(DetailView):
    model = Torrent
    template_name = 'bt/torrent_detail.html'
    context_object_name = 'torrent_detail'

    def get_context_data(self, **kwargs):
        # Get the existing context from the parent class
        context = super().get_context_data(**kwargs)

        # Get the current torrent object
        torrent = self.object

        # Add tracker details to the context (assuming a reverse relation through `TrackerStat`)
        context['tracker_detail'] = torrent.trackerstat_set.all()

        return context
    
class TorrentCreateView(LoginRequiredMixin, CreateView):
    model = Torrent
    fields = ['name', 'size', 'pieces', 'category']
    template_name = 'torrent/torrent_form.html'
    success_url = reverse_lazy('torrent_list')

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        messages.success(self.request, "Torrent created successfully.")
        return super().form_valid(form)

class TorrentUpdateView(LoginRequiredMixin, UpdateView):
    model = Torrent
    fields = ['name', 'size', 'pieces', 'category']
    template_name = 'torrent/torrent_form.html'
    success_url = reverse_lazy('torrent_list')

    def form_valid(self, form):
        messages.success(self.request, "Torrent updated successfully.")
        return super().form_valid(form)

class TorrentDeleteView(LoginRequiredMixin, DeleteView):
    model = Torrent
    template_name = 'torrent/torrent_confirm_delete.html'
    success_url = reverse_lazy('torrent_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Torrent deleted successfully.")
        return super().delete(request, *args, **kwargs)
