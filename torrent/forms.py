from django import forms
from .models import Category, Project, Torrent

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
