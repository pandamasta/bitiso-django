from django import forms
from .models import Category, Project, Torrent

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class SearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=100, min_length=2)

    def clean_query(self):
        query = self.cleaned_data.get('query')
        if len(query) < 2:
            raise forms.ValidationError("La recherche doit contenir au moins 2 caractères.")
        return query


class SetCategoryForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, label="Category")


class SetProjectForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        label="Project"
    )

class FileUploadForm(forms.Form):
    file = forms.FileField(label='Select a file')



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )