from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

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
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Fields the user can edit
