from django import forms
from .models import Category, Project, Torrent

from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class FileUploadForm(forms.Form):
    file = forms.FileField(label='Select a file')

class URLDownloadForm(forms.Form):
    url = forms.URLField(label='URL to Download')

class TorrentActionForm(forms.Form):
    torrent_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        required=False
    )
    action = forms.ChoiceField(
        choices=[('delete', 'Delete'), ('set_category', 'Set Category'), ('set_project', 'Set Project')],
        required=True
    )
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        torrent_choices = kwargs.pop('torrent_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['torrent_ids'].choices = torrent_choices

from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'website_url', 'website_url_download', 'website_url_repo', 'image']