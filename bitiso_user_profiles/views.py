from core.user_profiles.views import ProfileEditView, ProfileView
from .models import BitisoUserProfile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from torrents.models import Torrent
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class BitisoUserProfileView(ProfileView):
    def get_profile_model(self):
        return BitisoUserProfile
    
    def get_context_data(self, **kwargs):
        """Pass the profile object to the template."""
        context = super().get_context_data(**kwargs)
        # Ensure that the correct profile is being passed
        context['profile'] = self.get_object().bitisouserprofile # fetches the BitisoUserProfile associated with the user.

        return context


class BitisoUserProfileEditView(ProfileEditView):
    def get_profile_model(self):
        return BitisoUserProfile


@login_required
def user_torrent_dashboard(request, uuid=None, username=None):
    """
    Extend the generic dashboard to include torrent management for the user.
    """
    if settings.USE_UUID_FOR_PROFILE_URL and uuid:
        user = get_object_or_404(User, uuid=uuid)
    else:
        user = get_object_or_404(User, username=username)
    
    user_torrents = user.torrents.all()  # Fetch the user's torrents
    return render(request, 'bitiso_user_profiles/dashboard.html', {
        'user': user,
        'user_torrents': user_torrents
    })