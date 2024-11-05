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


logger = logging.getLogger(__name__)


# List view: Display all torrents
class TorrentListView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_list.html'
    context_object_name = 'torrents'
    paginate_by = 10  # If you want to paginate torrents


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

logger = logging.getLogger(__name__)


@login_required
def import_torrent_from_url(request):
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            tmp_file_path = None
            try:
                # Step 1: Download the torrent file
                logger.info(f"Downloading torrent from URL: {url}")
                response = requests.get(url)
                response.raise_for_status()

                # Save to a temporary file with a clear name
                original_filename = os.path.basename(urlparse(url).path) or "downloaded_torrent"
                tmp_file_path = os.path.join(tempfile.gettempdir(), f"{original_filename}_temp.torrent")
                with open(tmp_file_path, 'wb') as tmp_file:
                    tmp_file.write(response.content)
                logger.info(f"Temporary torrent file saved at: {tmp_file_path}")

                # Step 2: Process the torrent file
                metadata = process_torrent_file(tmp_file_path, request.user)
                if not metadata:
                    messages.error(request, "Failed to process the torrent file.")
                    return redirect('dashboard')

                # Ensure directory based on info hash for both original and processed files
                subdir_1, subdir_2 = metadata["info_hash"][:2], metadata["info_hash"][2:4]
                torrent_dir = os.path.join(settings.MEDIA_TORRENT, subdir_1, subdir_2)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, torrent_dir), exist_ok=True)

                # Define full paths for saving files
                original_full_path = os.path.join(settings.MEDIA_ROOT, torrent_dir, f"{metadata['name']}_original.torrent")
                processed_full_path = os.path.join(settings.MEDIA_ROOT, torrent_dir, f"{metadata['name']}_processed.torrent")

                # Save the original torrent file
                with open(original_full_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Original torrent file saved at: {original_full_path}")

                # Save the processed torrent file
                process_torrent_file(tmp_file_path, request.user, save_path=processed_full_path)
                logger.info(f"Processed torrent file saved at: {processed_full_path}")

                # Convert full paths to relative paths
                original_relative_path = os.path.relpath(original_full_path, settings.MEDIA_ROOT)
                processed_relative_path = os.path.relpath(processed_full_path, settings.MEDIA_ROOT)

                # Create the Torrent instance with relative paths
                torrent = Torrent(
                    info_hash=metadata["info_hash"],
                    name=metadata["name"],
                    slug=slugify(metadata["name"]),
                    original_file_path=original_relative_path,  # Store relative path
                    processed_file_path=processed_relative_path,  # Store relative path
                    website_url_download=url,
                    user=request.user,
                    size=metadata["size"],
                    pieces=metadata["pieces"],
                    piece_size=metadata["piece_size"],
                    magnet=metadata["magnet"],
                    torrent_filename=metadata["torrent_filename"],
                    file_list=metadata["file_list"],
                    file_count=metadata["file_count"]
                )
                torrent.save()

                # Link trackers
                _link_trackers_to_torrent(metadata["trackers"], torrent)

                messages.success(request, f"Torrent '{metadata['name']}' successfully imported.")
                return redirect('dashboard')

            except requests.RequestException as e:
                logger.error(f"Error downloading torrent from {url}: {e}")
                messages.error(request, f"Error downloading the torrent file: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
            finally:
                # Clean up the temporary file
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

    form = URLDownloadForm()
    return render(request, 'torrents/import_torrent_from_url.html', {'form': form})
def _link_trackers_to_torrent(trackers, torrent_obj):
    """
    Link each tracker URL to the Torrent object and set announce_priority.
    """
    for level, tracker_list in enumerate(trackers):
        for tracker_url in tracker_list:
            if tracker_url:
                # Get or create the tracker by URL
                tracker, created = Tracker.objects.get_or_create(url=tracker_url)
                # Link the tracker to the Torrent object
                torrent_obj.trackers.add(tracker)
                
                # Set announce_priority directly for each tracker in TrackerStat
                tracker_stat, _ = torrent_obj.trackerstat_set.get_or_create(
                    tracker=tracker,
                    defaults={'announce_priority': level}
                )
                tracker_stat.announce_priority = level
                tracker_stat.save()
                
                # Log the tracker link with announce_priority (level)
                logger.debug(f"Linked tracker {tracker_url} to torrent {torrent_obj.name} with announce_priority {level}")