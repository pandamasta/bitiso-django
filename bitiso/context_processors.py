# bitiso/context_processors.py
from django.conf import settings
from core.pages.models import Page
from django.contrib.auth import get_user_model
from torrents.models import Torrent, Project, Category


def project_name(request):
    return {
        'project_name': settings.PROJECT_NAME
    }

def page_list(request):
    """A context processor that returns all published pages, excluding the homepage."""
    pages = Page.objects.filter(is_published=True, is_homepage=False)
    return {'page_list': pages}

def profile_user(request):
    """Context processor to provide profile user."""
    if request.user.is_authenticated:
        return {'profile_user': request.user}
    return {'profile_user': None}


def use_uuid_for_profile_url(request):
    return {
        'USE_UUID_FOR_PROFILE_URL': settings.USE_UUID_FOR_PROFILE_URL
    }


def user_dashboard_counts(request):
    if request.user.is_authenticated:
        torrents_count = Torrent.objects.filter(user=request.user).count()
        projects_count = Project.objects.filter(user=request.user).count()
        categories_count = Category.objects.filter(user=request.user).count()
    else:
        torrents_count = 0
        projects_count = 0
        categories_count = 0

    return {
        'torrents_count': torrents_count,
        'projects_count': projects_count,
        'categories_count': categories_count,
    }


def gtag_processor(request):
    return {
        'GTAG_ENABLE': getattr(settings, 'GTAG_ENABLE', False),
        'GTAG_ID': getattr(settings, 'GTAG_ID', '')
    }