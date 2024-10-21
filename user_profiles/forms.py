# user_profiles/forms.py

from django import forms
from .models import UserProfile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'social_links', 'privacy_settings', 'notification_preferences', 'date_of_birth']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form appearance or behavior here if needed
