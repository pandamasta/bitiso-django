# torrents/views/category_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from ..models.torrent import Torrent
from ..models.category import Category
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from torrents.utils.query import validate_query

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
    pagination_count = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        query = self.request.GET.get('query', '').strip()
        sort_by = self.request.GET.get('sort_by', 'date')

        # Validate the query
        query_too_short = False
        query_too_long = False

        try:
            if query:
                query = validate_query(query, min_length=2, max_length=50)
        except ValidationError as e:
            if "at least" in str(e):
                query_too_short = True
            if "not exceed" in str(e):
                query_too_long = True
            query = ""  # Reset query if invalid

        # Filter torrents by category and active status
        torrents = Torrent.objects.filter(project__category=category, is_active=True)

        if query and not query_too_short and not query_too_long:
            torrents = torrents.filter(name__icontains=query)

        # Sorting
        if sort_by == 'seeds':
            torrents = torrents.order_by('-seed_count')
        elif sort_by == 'leeches':
            torrents = torrents.order_by('-leech_count')
        else:
            torrents = torrents.order_by('-created_at')

        # Pagination
        paginator = Paginator(torrents, self.pagination_count)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Add variables to context
        context['category'] = category
        context['torrents'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['query'] = query
        context['sort_by'] = sort_by
        context['query_too_short'] = query_too_short
        context['query_too_long'] = query_too_long

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
    
