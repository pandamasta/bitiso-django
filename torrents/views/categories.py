# torrents/views/category_views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


from ..models import Category
from ..forms import CategoryForm

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
    
