# pages/views.py

from django.views.generic import ListView, DetailView, UpdateView
from django.core.exceptions import ValidationError
from django.utils import translation
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from .models import Page
from .forms import PageForm

def redirect_to_language_home(request):
    user_language = translation.get_language()
    return redirect(f'/{user_language}/')

class HomePageView(DetailView):
    template_name = 'pages/home.html'  # Use a dynamic home template
    context_object_name = 'page'

    def get_object(self):
        try:
            # Try to get the homepage page object
            return Page.objects.get(is_published=True, is_homepage=True)
        except Page.DoesNotExist:
            return None  # No homepage exists, fallback to None

    def get(self, request, *args, **kwargs):
        # Check if a homepage exists
        page = self.get_object()

        if page:
            # If a homepage exists, render it
            context = {self.context_object_name: page}
            return self.render_to_response(context)
        else:
            # If no homepage exists, render a default template or message
            return render(request, 'pages/home.html', {
                'message': "No homepage is currently set. Please create a homepage in the admin panel."
            })

class PageDetailView(DetailView):
    model = Page
    template_name = "pages/page_detail.html"
    context_object_name = 'page'

    def get_object(self):
        # Fetch the page by slug and only show published pages unless user is logged in
        if self.request.user.is_authenticated:
            return get_object_or_404(Page, slug=self.kwargs['slug'])
        else:
            return get_object_or_404(Page, slug=self.kwargs['slug'], is_published=True)

class PageListView(ListView):
    """Displays a list of all published pages."""
    model = Page
    template_name = 'pages/page_list.html'
    context_object_name = 'pages'

    def get_queryset(self):
        """Return only published pages."""
        return Page.objects.filter(is_published=True)

@method_decorator(login_required, name='dispatch')
class PageUpdateView(UpdateView):
    model = Page
    form_class = PageForm
    template_name = "pages/page_edit.html"

    def get_object(self):
        return get_object_or_404(Page, slug=self.kwargs['slug'])

    def form_valid(self, form):
        try:
            form.instance.clean()  # Run validation
        except ValidationError as e:
            form.add_error(None, e)  # Add validation errors to form
            return self.form_invalid(form)

        form.save()
        return redirect(reverse('page_detail', kwargs={'slug': form.instance.slug}))
