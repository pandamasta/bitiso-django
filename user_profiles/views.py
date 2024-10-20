from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from .forms import ProfileEditForm  # Assuming you have a form to handle profile edits
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages

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



@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    template_name = 'user_profiles/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('profile_view')

    def get_object(self):
        """Return the currently logged-in user."""
        return self.request.user

    def form_valid(self, form):
        """Save the form and redirect to the profile view."""
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)
