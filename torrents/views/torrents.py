# torrents/views/torrents.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import requests
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
import os
import logging
import hashlib
import tempfile  # Import tempfile at the top of your file

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from torrents.utils.torrent_utils import process_torrent_file
#from torrents.utils.torrent_utils import process_torrent_file, _link_trackers_to_torrent

from ..models import Torrent,Tracker
from ..forms import TorrentForm
from ..forms import URLDownloadForm
from ..forms import FileUploadForm

from django.utils.text import slugify

import os
import tempfile
import uuid
import requests
from django.shortcuts import redirect
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from torrents.models import Torrent, Tracker
from torrents.utils.torrent_utils import process_torrent_file
import logging
import os
import tempfile
from django.conf import settings
from django.shortcuts import redirect
from django.utils.text import slugify
from urllib.parse import urlparse
import requests
from torf import Torrent as Torrenttorf


logger = logging.getLogger(__name__)


# List view: Display all torrents
class TorrentListView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_list.html'
    context_object_name = 'torrents'
    paginate_by = 40  # If you want to paginate torrents


    def get_queryset(self):
        # Return only active torrents (is_active=True)
        return Torrent.objects.filter(is_active=True)
    
    def get_object(self):
        # Ensure that the torrent with the provided slug exists
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))

# Detail view: Display details of a specific torrent
class TorrentDetailView(DetailView):
    model = Torrent
    template_name = 'torrents/torrent_detail.html'
    context_object_name = 'torrent'

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        # Get the existing context from the parent class
        context = super().get_context_data(**kwargs)

        # Get the current torrent object
        torrent = self.get_object()

        # Add tracker details to the context (assuming a reverse relation through `TrackerStat`)
        context['tracker_detail'] = torrent.trackerstat_set.all()

        return context

# Create view: Form for uploading a new torrent
class TorrentCreateView(LoginRequiredMixin,CreateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful creation

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Update view: Form for editing an existing torrent
class TorrentUpdateView(LoginRequiredMixin,UpdateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful update

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Delete view: Confirm and delete an existing torrent
class TorrentDeleteView(LoginRequiredMixin,DeleteView):
    model = Torrent
    template_name = 'torrents/torrent_confirm_delete.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful deletion

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    

    #############


@login_required
def upload_local_torrent(request):
    """
    View to handle uploading of a torrent file by a logged-in user.
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Ensure the directory exists
            torrent_dir = settings.MEDIA_TORRENT
            if not os.path.exists(torrent_dir):
                os.makedirs(torrent_dir)

            fs = FileSystemStorage(location=torrent_dir)
            filename = file.name

            if fs.exists(filename):
                messages.error(request, f"The file '{filename}' already exists. Please rename your file and try again.")
                return redirect('dashboard', username=request.user.username)

            saved_file_path = fs.save(file.name, file)
            torrent_file_path = os.path.join(settings.MEDIA_TORRENT, saved_file_path)

            try:
                process_torrent_file(torrent_file_path, request.user)
                messages.success(request, "Upload and import succeeded.")
            except ValidationError as e:
                messages.error(request, str(e))

            return redirect('dashboard', username=request.user.username)

    form = FileUploadForm()
    return render(request, 'torrents/upload_local_torrent.html', {'form': form})


@login_required
def import_torrent_from_url(request, use_info_hash_folders=True):
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            tmp_file_path = download_torrent(url)
            if not tmp_file_path:
                messages.error(request, "Error downloading the torrent file.")
                return redirect('dashboard')

            try:
                # Extract info_hash to check if torrent already exists
                info_hash = extract_info_hash(tmp_file_path)
                if not info_hash:
                    messages.error(request, "Failed to extract info hash from the torrent file.")
                    return redirect('dashboard')

                # Check if torrent with the same info_hash already exists
                if Torrent.objects.filter(info_hash=info_hash).exists():
                    messages.info(request, f"The torrent with info_hash {info_hash} already exists in the database.")
                    logger.info(f"Torrent with info_hash {info_hash} already exists. Skipping import.")
                    return redirect('dashboard')

                # Determine save directory based on settings
                save_dir = determine_save_dir(info_hash, use_info_hash_folders)

                # Process torrent file to get full metadata, using the specified save_dir
                metadata = process_torrent_file(tmp_file_path, save_dir=save_dir)
                if not metadata:
                    messages.error(request, "Failed to process the torrent file.")
                    return redirect('dashboard')

                # Create the Torrent instance
                torrent = create_torrent_instance(metadata, url, metadata["torrent_filename"], request.user)

                # Link trackers
                _link_trackers_to_torrent(metadata["trackers"], torrent)

                messages.success(request, f"Torrent '{metadata['name']}' successfully imported.")
                return redirect('dashboard')

            except Exception as e:
                logger.error(f"An error occurred while importing the torrent: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
            finally:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

    form = URLDownloadForm()
    return render(request, 'torrents/import_torrent_from_url.html', {'form': form})


def extract_info_hash(torrent_file_path):
    """Extracts the info_hash from a torrent file."""
    try:
        t = Torrenttorf.read(torrent_file_path)
        return t.infohash
    except Exception as e:
        logger.error(f"Error extracting info_hash from torrent file: {e}")
        return None


def download_torrent(url):
    """Télécharge le fichier torrent depuis une URL et retourne le chemin du fichier temporaire."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        original_filename = os.path.basename(urlparse(url).path) or "downloaded_torrent"
        tmp_file_path = os.path.join(tempfile.gettempdir(), f"{original_filename}_temp.torrent")
        with open(tmp_file_path, 'wb') as tmp_file:
            tmp_file.write(response.content)
        return tmp_file_path
    except requests.RequestException as e:
        logger.error(f"Error downloading torrent from {url}: {e}")
        return None


def determine_save_dir(info_hash, use_info_hash_folders):
    """Determines the directory for saving torrent files."""
    if use_info_hash_folders:
        subdir_1, subdir_2 = info_hash[:2], info_hash[2:4]
        torrent_dir = os.path.join(settings.MEDIA_TORRENT, subdir_1, subdir_2)
    else:
        torrent_dir = settings.MEDIA_TORRENT
    os.makedirs(os.path.join(settings.MEDIA_ROOT, torrent_dir), exist_ok=True)
    return torrent_dir


def create_torrent_instance(metadata, url, torrent_filename, user):
    """Creates and saves a Torrent instance in the database."""
    torrent = Torrent(
        info_hash=metadata["info_hash"],
        name=metadata["name"],
        slug=slugify(metadata["name"]),
        torrent_filename=torrent_filename,
        website_url_download=url,
        user=user,
        size=metadata["size"],
        pieces=metadata["pieces"],
        piece_size=metadata["piece_size"],
        magnet=metadata["magnet"],
        file_list=metadata["file_list"],
        file_count=metadata["file_count"]
    )
    torrent.save()
    return torrent


def _link_trackers_to_torrent(trackers, torrent_obj):
    """Link each tracker URL to the Torrent object and set announce_priority."""
    for level, tracker_list in enumerate(trackers):
        for tracker_url in tracker_list:
            if tracker_url:
                try:
                    # Get or create the tracker by URL
                    tracker, created = Tracker.objects.get_or_create(url=tracker_url)
                    torrent_obj.trackers.add(tracker)
                    
                    # Set announce_priority directly for each tracker in TrackerStat
                    tracker_stat, _ = torrent_obj.trackerstat_set.get_or_create(
                        tracker=tracker,
                        defaults={'announce_priority': level}
                    )
                    tracker_stat.announce_priority = level
                    tracker_stat.save()
                    logger.debug(f"Linked tracker {tracker_url} to torrent {torrent_obj.name} with announce_priority {level}")
                
                except Exception as e:
                    logger.error(f"Failed to link tracker {tracker_url} to torrent {torrent_obj.name}: {e}")


