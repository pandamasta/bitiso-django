from core.user_profiles.views import ProfileEditView, ProfileView
from .models import BitisoUserProfile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from torrents.models import Torrent, Project, Category
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

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
    View that handles the user dashboard, showing the counts of torrents, projects, and categories
    along with the lists for categories and projects to use in the dashboard form.
    """
    # # Get torrents, projects, and categories related to the user
    # user_torrents = Torrent.objects.filter(user=request.user)
    # user_projects = Project.objects.filter(user=request.user)
    # user_categories = Category.objects.filter(user=request.user)

    # # Count the items for display
    # torrents_count = user_torrents.count()
    # projects_count = user_projects.count()
    # categories_count = user_categories.count()

    # # Pass categories and projects to the form as well
    # categories = Category.objects.all()  # Assuming you want all categories, adjust if needed
    # projects = Project.objects.all()  # Assuming you want all projects, adjust if needed

    return render(request, 'bitiso_user_profiles/dashboard.html')



@login_required
def user_torrents(request):

    user_torrents = Torrent.objects.filter(user=request.user)
    projects = Project.objects.all()
    categories = Category.objects.all()
    # user_projects = Project.objects.filter(user=request.user)
    # user_categories = Category.objects.filter(user=request.user)

    return render(request, 'bitiso_user_profiles/torrents.html', {
        'user_torrents': user_torrents,
        'categories': categories,  # Add categories to the context
        'projects': projects,  # Add projects to the context
        })

@login_required
def user_projects(request):
    user_projects = Project.objects.filter(user=request.user)
    return render(request, 'bitiso_user_profiles/projects.html', {'user_projects': user_projects})

@login_required
def user_categories(request):
    user_categories = Category.objects.filter(user=request.user)
    return render(request, 'bitiso_user_profiles/categories.html', {'user_categories': user_categories})

