# torrents/views/category_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from ..models.torrent import Torrent
from ..models.category import Category
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the category based on the slug
        category = self.get_object()
        query = self.request.GET.get('query', '').strip()

        # Filter torrents related to the category
        related_torrents = Torrent.objects.filter(
            project__category=category,
            is_active=True
        ).select_related('project')

        # Handle query validation
        query_too_short = False
        if query:
            if len(query) < 2:  # Minimum 2-character search
                query_too_short = True
                related_torrents = Torrent.objects.none()
            else:
                related_torrents = related_torrents.filter(name__icontains=query)

        # Paginate torrents
        paginator = Paginator(related_torrents, 10)  # Show 10 torrents per page
        page_number = self.request.GET.get('page')
        context['torrents'] = paginator.get_page(page_number)

        # Add context variables
        context['query'] = query
        context['query_too_short'] = query_too_short

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
    
