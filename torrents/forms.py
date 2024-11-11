# torrents/forms.py

from django import forms
from django.core.exceptions import ValidationError

from .models import Torrent, Project, Category, Tracker
from django.conf import settings


class TorrentForm(forms.ModelForm):
    readonly_fields = ['info_hash', 'size', 'pieces', 'piece_size', 'file_list', 'file_count',
                       'magnet', 'torrent_file_path', 'website_url_download', 'created_at', 'updated_at']

    class Meta:
        model = Torrent
        fields = [
            'name','slug', 'comment', 'category', 
            'is_active', 'description', 'website_url', 
            'website_url_repo', 'version'
        ]

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'is_active', 'description', 'website_url', 'website_url_download', 'website_url_repo', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image', None)
        if image:
            if image.size > 2 * 1024 * 1024:  # Limit file size to 2MB
                raise forms.ValidationError("Image size should not exceed 2MB.")
        return image

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent_category']  
        
class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ['url']


# Ensure the max size is loaded from settings
MAX_FILE_SIZE_MB = getattr(settings, 'MAX_FILE_SIZE_MB', 5)  # Default to 5 MB

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select a torrent file")

    def clean_file(self):
        file = self.cleaned_data.get('file')

        # Check file extension for .torrent
        if not file.name.endswith('.torrent'):
            raise ValidationError("Only .torrent files are allowed.")

        # Check file size limit
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"File size must be under {MAX_FILE_SIZE_MB} MB.")

        return file
    
class URLDownloadForm(forms.Form):
    url = forms.URLField(label="Download from URL", max_length=2000)