# torrents/views/category_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from ..models.torrent import Torrent
from ..models.category import Category


from ..models import Category
from ..forms import CategoryForm

# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'torrents/category_list.html'
    context_object_name = 'categories'

    #def get_queryset(self):
        # Fetch only top-level categories and prefetch their children
    #    return Category.objects.filter(parent_category__isnull=True).prefetch_related('children')
    def get_queryset(self):
        # Fetch only top-level categories and prefetch their children, ordered by `order` field
        return Category.objects.filter(parent_category__isnull=True).prefetch_related(
            'children'
        ).order_by('order', 'name')  # Explicitly order by `order`

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'torrents/category_detail.html'
    context_object_name = 'category'

    def get_object(self):
        # Fetch the category based on the slug
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch torrents related to the category and filter by is_active=True
        category = self.get_object()
        related_torrents = Torrent.objects.filter(
            project__category=category,
            is_active=True
        ).select_related('project')

        context['torrents'] = related_torrents
        return context
    
class CategoryCreateView(LoginRequiredMixin,CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
class CategoryUpdateView(LoginRequiredMixin,UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'torrents/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
class CategoryDeleteView(LoginRequiredMixin,DeleteView):
    model = Category
    template_name = 'torrents/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('slug'))
    
