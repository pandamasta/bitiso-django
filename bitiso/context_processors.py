# bitiso/context_processors.py
from django.conf import settings
from pages.models import Page

def project_name(request):
    return {
        'project_name': settings.PROJECT_NAME
    }

def page_list(request):
    """A context processor that returns all published pages, excluding the homepage."""
    pages = Page.objects.filter(is_published=True, is_homepage=False)
    return {'page_list': pages}
