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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..utils.torrent_utils import process_torrent_file
from ..models import Torrent
from ..forms import TorrentForm
from ..forms import URLDownloadForm
from ..forms import FileUploadForm

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

@login_required
def import_torrent_from_url(request):
    """
    View to handle downloading a torrent from a URL, saving it, and creating a user-friendly symlink.
    """
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                # Step 1: Download the torrent file from the provided URL
                logger.info(f"Starting download of torrent from URL: {url}")
                response = requests.get(url)
                response.raise_for_status()

                # Save the downloaded content as a ContentFile object for Django handling
                content = ContentFile(response.content)
                parsed_url = urlparse(url)
                original_filename = parsed_url.path.split('/')[-1]
                
                # Step 2: Generate a hash-based directory structure to store the torrent file
                # This keeps files organized for scalability
                file_hash = hashlib.sha1(content.read()).hexdigest()  # Generate SHA-1 hash of content
                subdir_1, subdir_2 = file_hash[0], file_hash[1]
                torrent_directory = os.path.join(settings.MEDIA_TORRENT, subdir_1, subdir_2)
                content.seek(0)  # Reset content pointer for saving
                
                # Ensure the directory exists
                if not os.path.exists(torrent_directory):
                    os.makedirs(torrent_directory)
                    logger.info(f"Created directory structure for torrent: {torrent_directory}")

                # Step 3: Save the original torrent file in the organized directory
                fs = FileSystemStorage(location=torrent_directory)
                original_path = fs.save(f"{original_filename}_original.torrent", content)
                original_full_path = os.path.join(torrent_directory, original_path)
                logger.info(f"Original torrent file saved at: {original_full_path}")

                # Step 4: Process the torrent and save a modified version with Bitiso tracker included
                # Define the processed file path with a suffix for clarity
                processed_filename = f"{original_filename}_processed.torrent"
                processed_file_path = os.path.join(torrent_directory, processed_filename)
                process_torrent_file(original_full_path, request.user, source_url=url, save_path=processed_file_path)

                # Step 5: Create a user-friendly symlink in the main media directory
                simple_symlink_path = os.path.join(settings.MEDIA_ROOT, original_filename)
                if not os.path.exists(simple_symlink_path):
                    os.symlink(processed_file_path, simple_symlink_path)
                    logger.info(f"Created user-friendly symlink at {simple_symlink_path} -> {processed_file_path}")

                messages.success(request, "Download, upload, and import succeeded.")

            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading torrent from {url}: {str(e)}")
                messages.error(request, f"Error downloading file: {e}")
            except ValidationError as e:
                logger.error(f"Validation error processing torrent: {str(e)}")
                messages.error(request, f"Error processing torrent: {e}")
            except Exception as e:
                logger.error(f"Unexpected error occurred: {str(e)}")
                messages.error(request, f"An unexpected error occurred: {e}")

            # Redirect to the user-specific dashboard after processing
            return redirect('dashboard')

    form = URLDownloadForm()
    return render(request, 'torrents/import_torrent_from_url.html', {'form': form})


