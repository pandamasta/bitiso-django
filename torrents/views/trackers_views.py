from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ..models import Tracker
from ..forms import TrackerForm

# Tracker Views
class TrackerListView(ListView):
    model = Tracker
    template_name = 'torrents/tracker_list.html'
    context_object_name = 'trackers'

    def get_object(self):
        return get_object_or_404(Tracker, slug=self.kwargs.get('slug'))
    
class TrackerDetailView(DetailView):
    model = Tracker
    template_name = 'torrents/tracker_detail.html'
    context_object_name = 'tracker'

    def get_object(self):
        return get_object_or_404(Tracker, slug=self.kwargs.get('slug'))
    
class TrackerCreateView(CreateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'torrents/tracker_form.html'
    success_url = reverse_lazy('tracker_list')

    def get_object(self):
        return get_object_or_404(Tracker, slug=self.kwargs.get('slug'))
    
class TrackerUpdateView(UpdateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'torrents/tracker_form.html'
    success_url = reverse_lazy('tracker_list')

    def get_object(self):
        return get_object_or_404(Tracker, slug=self.kwargs.get('slug'))
    
class TrackerDeleteView(DeleteView):
    model = Tracker
    template_name = 'torrents/tracker_confirm_delete.html'
    success_url = reverse_lazy('tracker_list')

    def get_object(self):
        return get_object_or_404(Tracker, slug=self.kwargs.get('slug'))
