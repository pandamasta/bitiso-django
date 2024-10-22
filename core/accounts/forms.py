# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django import forms
from django.conf import settings

# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser  # Link the form to the CustomUser model
        fields = ('username', 'email')  # Fields to display in the form
        labels = {
            'username': _('Username'),
            'email': _('Email address'),
            'password1': _('Password'),
            'password2': _('Confirm Password'),
        }


# Custom User Update Form
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean_username(self):
        """Check if the username can be changed based on the last change."""
        user = self.instance
        new_username = self.cleaned_data.get('username')
        if new_username != user.username:
            time_since_last_change = timezone.now() - user.username_last_changed
            if time_since_last_change < timedelta(days=settings.USERNAME_CHANGE_LIMIT_DAYS):
                raise forms.ValidationError(
                    f"Username can only be changed every {settings.USERNAME_CHANGE_LIMIT_DAYS} days."
                )
        return new_username
