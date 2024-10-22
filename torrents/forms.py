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

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent_category']  
        
class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ['url']