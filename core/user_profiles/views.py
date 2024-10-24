from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from .forms import ProfileEditForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from .models import AbstractUserProfile

User = get_user_model()

class ProfileView(DetailView):
    model = User
    template_name = 'user_profiles/profile_detail.html'
    context_object_name = 'profile_user'

    def get_object(self):
        """Return the user object based on the provided username or uuid."""
        if settings.USE_UUID_FOR_PROFILE_URL:
            return get_object_or_404(User, uuid=self.kwargs.get('uuid'))
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        """Pass the profile object to the template."""
        context = super().get_context_data(**kwargs)
        # Fetch the BitisoUserProfile related to the user
        context['profile'] = self.get_object().bitisouserprofile
        return context
    
@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    template_name = 'user_profiles/profile_edit.html'
    form_class = ProfileEditForm
    context_object_name = 'profile_user'

    def get_object(self):
        """
        Dynamically get the profile based on UUID or username.
        The profile model is obtained from the extending app via get_profile_model.
        """
        ProfileModel = self.get_profile_model()  # Dynamically get the concrete profile model
        if settings.USE_UUID_FOR_PROFILE_URL:
            return get_object_or_404(ProfileModel, user__uuid=self.kwargs.get('uuid'))
        return get_object_or_404(ProfileModel, user__username=self.kwargs.get('username'))

    def get_profile_model(self):
        """
        Return the profile model.
        This should be overridden by the app extending the core profile.
        """
        raise NotImplementedError("You need to define the get_profile_model method in your app.")

    def get_success_url(self):
        """Redirect to the correct profile view after a successful update."""
        if settings.USE_UUID_FOR_PROFILE_URL:
            return reverse_lazy('profile_view', kwargs={'uuid': self.request.user.uuid})
        return reverse_lazy('profile_view', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        """Save the form and redirect to the profile view."""
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)