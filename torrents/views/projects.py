# torrents/views/torrents_project.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count
from ..models.category import Category
from ..models.project import Project
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from ..models import Project, Torrent
from ..forms import ProjectForm

class ProjectListView(ListView):
    model = Project
    template_name = 'torrents/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10  # Set pagination for flat project results

    def get_queryset(self):
        """
        Handle both default project listing and search queries.
        """
        query = self.request.GET.get('query', '').strip()
        projects = Project.objects.filter(is_active=True)

        if query:
            # Filter projects by name or description containing the query
            return projects.filter(name__icontains=query)
        
        return projects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add query to the context for use in the search bar
        query = self.request.GET.get('query', '').strip()
        context['query'] = query

        # Add the number of results if a query is present
        if query:
            context['result_count'] = self.get_queryset().count()

        if not query:  # Only group by category if there's no query
            categories = Category.objects.all()
            context['categories'] = categories
            category_projects = {
                category: Project.objects.filter(category=category, is_active=True)
                for category in categories
            }
            context['category_projects'] = category_projects

        return context

    
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'torrents/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        query = self.request.GET.get('query', '').strip()
        sort_by = self.request.GET.get('sort_by', 'date')  # Default sorting by date
        related_torrents = Torrent.objects.filter(project=project, is_active=True)

        # Handle query validation
        query_too_short = False
        if query:
            if len(query) < 2:  # Minimum 2-character search
                query_too_short = True
                related_torrents = Torrent.objects.none()
            else:
                related_torrents = related_torrents.filter(name__icontains=query)

        # Apply sorting
        if sort_by == 'seeds':
            related_torrents = related_torrents.order_by('-seed_count')
        elif sort_by == 'leeches':
            related_torrents = related_torrents.order_by('-leech_count')
        else:  # Default to sorting by date
            related_torrents = related_torrents.order_by('-created_at')

        # Paginate torrents
        paginator = Paginator(related_torrents, 10)
        page_number = self.request.GET.get('page')
        context['torrents'] = paginator.get_page(page_number)

        # Add extra context
        context['project'] = project
        context['query'] = query
        context['sort_by'] = sort_by
        context['query_too_short'] = query_too_short

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

