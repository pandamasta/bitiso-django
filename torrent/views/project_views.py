# views/project_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Project
from ..forms import ProjectForm

class ProjectListView(ListView):
    model = Project
    template_name = 'project/project_list.html'
    context_object_name = 'projects'
    paginate_by = 40

    def get_queryset(self):
        return Project.objects.filter(is_active=True).order_by('-creation')

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['torrents'] = self.object.torrents.all().order_by('-creation')
        return context

class ProjectDetailByIdView(DetailView):
    model = Project
    template_name = 'project/project_detail.html'
    context_object_name = 'project'

    def get_object(self, queryset=None):
        return get_object_or_404(Project, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['torrents'] = self.object.torrents.all().order_by('-creation')
        return context


class ProjectDetailBySlugView(DetailView):
    model = Project
    template_name = 'project/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'project_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the related torrents to the context
        context['torrents'] = self.object.torrents.all().order_by('-creation')
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_form.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Project created successfully.")
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_form.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully.")
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'project/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Project deleted successfully.")
        return super().delete(request, *args, **kwargs)

