from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Torrent, Project, Category, Tracker
from .forms import TorrentForm
from .forms import ProjectForm, CategoryForm, TrackerForm


# List view: Display all torrents
class TorrentListView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_list.html'
    context_object_name = 'torrents'
    paginate_by = 10  # If you want to paginate torrents

# Detail view: Display details of a specific torrent
class TorrentDetailView(DetailView):
    model = Torrent
    template_name = 'torrents/torrent_detail.html'
    context_object_name = 'torrent'

# Create view: Form for uploading a new torrent
class TorrentCreateView(CreateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful creation

# Update view: Form for editing an existing torrent
class TorrentUpdateView(UpdateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful update

# Delete view: Confirm and delete an existing torrent
class TorrentDeleteView(DeleteView):
    model = Torrent
    template_name = 'torrents/torrent_confirm_delete.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful deletion



# Project Views
class ProjectListView(ListView):
    model = Project
    template_name = 'torrents/project_list.html'
    context_object_name = 'projects'

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'torrents/project_detail.html'
    context_object_name = 'project'

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'torrents/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')


# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'torrents/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'torrents/category_detail.html'
    context_object_name = 'category'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'torrents/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')


# Tracker Views
class TrackerListView(ListView):
    model = Tracker
    template_name = 'torrents/tracker_list.html'
    context_object_name = 'trackers'

class TrackerDetailView(DetailView):
    model = Tracker
    template_name = 'torrents/tracker_detail.html'
    context_object_name = 'tracker'

class TrackerCreateView(CreateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'torrents/tracker_form.html'
    success_url = reverse_lazy('tracker_list')

class TrackerUpdateView(UpdateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'torrents/tracker_form.html'
    success_url = reverse_lazy('tracker_list')

class TrackerDeleteView(DeleteView):
    model = Tracker
    template_name = 'torrents/tracker_confirm_delete.html'
    success_url = reverse_lazy('tracker_list')