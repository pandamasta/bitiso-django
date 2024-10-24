# user_profiles/forms.py

from django import forms
from .models import AbstractUserProfile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = AbstractUserProfile
        fields = ['profile_picture', 'bio' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form appearance or behavior here if needed
