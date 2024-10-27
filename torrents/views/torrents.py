# torrents/views/torrents.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from ..models import Torrent
from ..forms import TorrentForm

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
class TorrentCreateView(CreateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful creation

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Update view: Form for editing an existing torrent
class TorrentUpdateView(UpdateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful update

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    
# Delete view: Confirm and delete an existing torrent
class TorrentDeleteView(DeleteView):
    model = Torrent
    template_name = 'torrents/torrent_confirm_delete.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful deletion

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))
    

    #############

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
#from ..models import Torrent, Project, Category, Tracker
from ..forms import TorrentForm
#from ..forms import ProjectForm, CategoryForm, TrackerForm
from django.shortcuts import get_object_or_404
from django.conf import settings
from torrents import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from ..forms import FileUploadForm
import requests
from ..forms import URLDownloadForm
from ..utils.torrent_utils import process_torrent_file
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
import os
import logging


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



logger = logging.getLogger(__name__)



@login_required
def import_torrent_from_url(request):
    """
    View to handle downloading a torrent from a URL and importing it.
    """
    if request.method == 'POST':
        form = URLDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                logger.info(f"Downloading torrent from URL: {url}")
                response = requests.get(url)
                response.raise_for_status()

                content = ContentFile(response.content)
                parsed_url = urlparse(url)
                original_filename = parsed_url.path.split('/')[-1]
                filename = original_filename

                # Ensure the MEDIA_TORRENT directory exists
                torrent_directory = settings.MEDIA_TORRENT
                if not os.path.exists(torrent_directory):
                    os.makedirs(torrent_directory)
                    logger.info(f"Created directory: {torrent_directory}")
                else:
                    logger.info(f"Torrent directory already exists: {torrent_directory}")

                fs = FileSystemStorage(location=torrent_directory)

                # Check if the file already exists in the filesystem and handle conflicts
                counter = 1
                while fs.exists(filename):
                    logger.warning(f"The file '{filename}' already exists in the filesystem. Renaming.")
                    filename = f"{os.path.splitext(original_filename)[0]}_{counter}{os.path.splitext(original_filename)[1]}"
                    counter += 1

                # Save the torrent file
                logger.info(f"Saving torrent file as: {filename}")
                saved_file_path = fs.save(filename, content)
                torrent_file_path = os.path.join(torrent_directory, saved_file_path)
                logger.info(f"Torrent file saved at: {torrent_file_path}")

                # Process the torrent file
                process_torrent_file(torrent_file_path, request.user, source_url=url)
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

            # Redirect to the user-specific dashboard
            user_uuid = request.user.uuid
            # return redirect('dashboard', uuid=user_uuid)
            return redirect('dashboard')

    form = URLDownloadForm()
    return render(request, 'torrents/import_torrent_from_url.html', {'form': form})

