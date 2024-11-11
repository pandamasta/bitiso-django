# torrents/views/torrents.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
import logging
import tempfile  

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from torrents.utils.torrent_utils import process_torrent_file

from ..models import Torrent
from ..forms import TorrentForm
from ..forms import URLDownloadForm
from ..forms import FileUploadForm

# from torrents.models import Torrent

from torf import Torrent as Torrenttorf

from torrents.utils.torrent_utils import (
    extract_info_hash,
    download_torrent,
    determine_save_dir,
    create_torrent_instance,
    _link_trackers_to_torrent,
    process_torrent_file
)


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
class TorrentUpdateView(LoginRequiredMixin, UpdateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful update

    def get_object(self):
        return get_object_or_404(Torrent, slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the Torrent instance directly to the template as 'torrent' for read-only display
        context['torrent'] = self.get_object()
        return context

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
            file = form.cleaned_data['file']

            # Save the uploaded file temporarily
            tmp_file_path = os.path.join(tempfile.gettempdir(), file.name)
            with open(tmp_file_path, 'wb+') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)

            try:
                # Extract info_hash to check if torrent already exists
                info_hash = extract_info_hash(tmp_file_path)
                if not info_hash:
                    messages.error(request, "Failed to extract info hash from the torrent file.")
                    return redirect('dashboard')

                # Check for existing torrent with the same info_hash
                if Torrent.objects.filter(info_hash=info_hash).exists():
                    messages.info(request, f"The torrent with info_hash {info_hash} already exists in the database.")
                    logger.info(f"Torrent with info_hash {info_hash} already exists. Skipping import.")
                    return redirect('dashboard')

                # Determine save directory based on info_hash
                save_dir = determine_save_dir(info_hash, use_info_hash_folders=True)

                # Process the torrent file to get metadata and save it
                metadata = process_torrent_file(tmp_file_path, save_dir=save_dir)
                if not metadata:
                    messages.error(request, "Failed to process the torrent file.")
                    return redirect('dashboard')

                # Save torrent instance in the database
                torrent = create_torrent_instance(metadata, "", metadata["torrent_file_path"], request.user)

                # Link trackers to the torrent
                _link_trackers_to_torrent(metadata["trackers"], torrent)

                messages.success(request, f"Torrent '{metadata['name']}' successfully imported.")
                return redirect('dashboard')

            except Exception as e:
                logger.error(f"An error occurred while importing the torrent: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

    else:
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
                torrent = create_torrent_instance(metadata, url, metadata["torrent_file_path"], request.user)

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

