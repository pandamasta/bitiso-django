from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Torrent, Project, Category, Tracker
from .forms import TorrentForm
from .forms import ProjectForm, CategoryForm, TrackerForm
from django.shortcuts import get_object_or_404
from django.conf import settings
from torrents import views
from django.contrib.auth.mixins import LoginRequiredMixin


# List view: Display all torrents
class TorrentListView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_list.html'
    context_object_name = 'torrents'
    paginate_by = 10  # If you want to paginate torrents

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))

# Detail view: Display details of a specific torrent
class TorrentDetailView(DetailView):
    model = Torrent
    template_name = 'torrents/torrent_detail.html'
    context_object_name = 'torrent'

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Create view: Form for uploading a new torrent
class TorrentCreateView(CreateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful creation

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Update view: Form for editing an existing torrent
class TorrentUpdateView(UpdateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful update

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Delete view: Confirm and delete an existing torrent
class TorrentDeleteView(DeleteView):
    model = Torrent
    template_name = 'torrents/torrent_confirm_delete.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful deletion

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))

# Project Views
class ProjectListView(ListView):
    model = Project
    template_name = 'torrents/project_list.html'
    context_object_name = 'projects'

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'torrents/project_detail.html'
    
    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the logged-in user
        return super().form_valid(form)

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'torrents/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))


# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'torrents/category_list.html'
    context_object_name = 'categories'

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'torrents/category_detail.html'
    context_object_name = 'category'

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'torrents/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
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