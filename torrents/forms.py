# torrents/forms.py

from django import forms
from .models import Torrent

class TorrentForm(forms.ModelForm):
    class Meta:
        model = Torrent
        fields = ['name', 'slug', 'size', 'pieces', 'piece_size', 'magnet', 'torrent_filename', 'comment', 'category', 'file_list', 'file_count', 'is_active', 'description', 'website_url', 'website_url_download', 'website_url_repo', 'version']
