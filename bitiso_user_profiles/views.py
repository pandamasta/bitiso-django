from core.user_profiles.views import ProfileEditView, ProfileView
from .models import BitisoUserProfile

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
