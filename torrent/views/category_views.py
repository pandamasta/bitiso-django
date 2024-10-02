# views/category_views.py

from django.views.generic import ListView
from ..models import Category, Torrent

class CategoryListView(ListView):
    model = Category
    template_name = 'category/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(ListView):
    model = Torrent
    template_name = 'category/category_detail.html'
    context_object_name = 'torrent_list'
    paginate_by = 40

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Torrent.objects.filter(is_active=True, category=self.category).order_by('-creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
