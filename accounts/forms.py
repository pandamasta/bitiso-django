from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms

# Form for user registration
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Add any custom fields you want here

# User update form
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # Add any fields you want users to edit

