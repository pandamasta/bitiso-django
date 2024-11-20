# torrents/views/torrents_project.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count
from ..models.category import Category
from ..models.project import Project

from ..models import Project, Torrent
from ..forms import ProjectForm

class ProjectListView(ListView):
    model = Project
    template_name = 'torrents/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        """
        Return only active projects (is_active=True) without dynamic annotations.
        """
        return Project.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve categories and group projects under each category
        categories = Category.objects.all()
        context['categories'] = categories
        # For each category, filter active projects using the pre-calculated torrent_count field
        category_projects = {
            category: Project.objects.filter(category=category, is_active=True)
            for category in categories
        }
        context['category_projects'] = category_projects
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'torrents/project_detail.html'
    
    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the project instance
        project = self.get_object()
        
        # Get related torrents and paginate them
        related_torrents = Torrent.objects.filter(project=project)
        paginator = Paginator(related_torrents, 10)  # Show 10 torrents per page
        page_number = self.request.GET.get('page')
        context['torrents'] = paginator.get_page(page_number)
        
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the logged-in user
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin,UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'torrents/project_form.html'
    success_url = reverse_lazy('project_list')

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

class ProjectDeleteView(LoginRequiredMixin,DeleteView):
    model = Project
    template_name = 'torrents/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

