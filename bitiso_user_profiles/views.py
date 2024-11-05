from core.user_profiles.views import ProfileEditView, ProfileView
from .models import BitisoUserProfile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from torrents.models import Torrent, Project, Category
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .actions import bulk_project_action
from django.shortcuts import render
from django.db.models import Count, Q  # Import Q for filtering


User = get_user_model()

class BitisoUserProfileView(ProfileView):

    def get_profile_model(self):
        return BitisoUserProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()  # Get the user object (e.g., CustomUser)
        
        # Ensure the profile exists or create it if missing
        if not hasattr(user, 'bitisouserprofile'):
            # Create the profile if it doesn't exist
            BitisoUserProfile.objects.create(user=user)
            context['profile'] = user.bitisouserprofile
        else:
            context['profile'] = user.bitisouserprofile

        return context

class BitisoUserProfileEditView(ProfileEditView):
    def get_profile_model(self):
        return BitisoUserProfile

    #user_categories = Category.objects.filter(user=request.user)

@login_required
def user_dashboard(request):
    """
    Main view of dashboard/
    """
    return render(request, 'bitiso_user_profiles/dashboard.html')

@login_required
def user_torrents(request):
    """
    View that show the user torrent and related bukl actions 
    """
    user_torrents = Torrent.objects.all()
    projects = Project.objects.all()
    categories = Category.objects.all()
    # user_torrents = Torrent.objects.filter(user=request.user)
    # user_projects = Project.objects.filter(user=request.user)
    # user_categories = Category.objects.filter(user=request.user)

    return render(request, 'bitiso_user_profiles/torrents.html', {
        'user_torrents': user_torrents,
        'categories': categories,  # Add categories to the context
        'projects': projects,  # Add projects to the context
        })

@login_required
def user_projects(request):
    # Get all projects for the current user, regardless of active status, and annotate active torrent count
    user_projects = Project.objects.filter(user=request.user).annotate(
        torrent_count=Count('torrents', filter=Q(torrents__is_active=True))
    )

    return render(request, 'bitiso_user_profiles/projects.html', {'user_projects': user_projects})

@login_required
def user_categories(request):
    # Retrieve categories created by the user, including any subcategories
    user_categories = Category.objects.filter(user=request.user, parent_category__isnull=True).prefetch_related('children')
    return render(request, 'bitiso_user_profiles/categories.html', {'user_categories': user_categories})