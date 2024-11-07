# torrents/forms.py

from django import forms
from .models import Torrent, Project, Category, Tracker



class TorrentForm(forms.ModelForm):
    class Meta:
        model = Torrent
        fields = ['name', 'slug', 'size', 'pieces', 'piece_size', 'magnet', 'torrent_filename', 'comment', 'category', 'file_list', 'file_count', 'is_active', 'description', 'website_url', 'website_url_download', 'website_url_repo', 'version']


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


class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select a .torrent file")


class URLDownloadForm(forms.Form):
    url = forms.URLField(label="Download from URL", max_length=2000)
