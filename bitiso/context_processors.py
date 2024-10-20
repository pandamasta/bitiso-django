# bitiso/context_processors.py
from django.conf import settings
from pages.models import Page
from django.contrib.auth import get_user_model


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