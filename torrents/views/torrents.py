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
from django.core.files import File
from django.http import FileResponse, Http404
from django.db.models import Q
from django.db.models import Count
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from torrents.utils.query import validate_query
from django.core.exceptions import ValidationError

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

class TorrentListView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_list.html'
    context_object_name = 'torrents'
    pagination_count = settings.PAGINATION_COUNT

    def get_queryset(self):
        """
        Fetch and filter torrents based on query parameters.
        """
        query = self.request.GET.get('query', '').strip()  # Clean whitespace
        sort_by = self.request.GET.get('sort_by', 'date')
        torrents = Torrent.objects.filter(is_active=True)  # Filter only active torrents
        query_too_short = False
        query_too_long = False

        # Validate the query
        try:
            if query:
                query = validate_query(query, min_length=2, max_length=50)
        except ValidationError as e:
            if "at least" in str(e):
                query_too_short = True
            if "not exceed" in str(e):
                query_too_long = True
            query = ""  # Reset query if invalid

        # Validate the sort_by parameter
        valid_sort_options = ['date', 'seeds', 'leeches']
        if sort_by not in valid_sort_options:
            sort_by = 'date'  # Default to 'date' if invalid

        # Apply query filtering
        if query and not query_too_short and not query_too_long:
            torrents = torrents.filter(name__icontains=query)

        # Apply sorting
        if sort_by == 'seeds':
            torrents = torrents.order_by('-seed_count')
        elif sort_by == 'leeches':
            torrents = torrents.order_by('-leech_count')
        else:  # Default to sorting by date
            torrents = torrents.order_by('-created_at')

        # Track state for context
        self.query_too_short = query_too_short
        self.query_too_long = query_too_long
        self.query = query
        self.sort_by = sort_by

        return torrents

    def get_context_data(self, **kwargs):
        """
        Add pagination and other context variables.
        """
        context = super().get_context_data(**kwargs)
        torrents = self.get_queryset()

        # Handle pagination
        paginator = Paginator(torrents, self.pagination_count)
        page_number = self.request.GET.get('page', 1)  # Default to the first page
        page_obj = paginator.get_page(page_number)

        # Add additional context
        context['torrents'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['query'] = self.query
        context['sort_by'] = self.sort_by
        context['query_too_short'] = self.query_too_short
        context['query_too_long'] = self.query_too_long

        return context

    
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

        # Add the base filename to the context
        if torrent.torrent_file:
            context['filename'] = os.path.basename(torrent.torrent_file.name)
        else:
            context['filename'] = None

        return context

# Create view: Form for uploading a new torrent
class TorrentCreateView(LoginRequiredMixin,CreateView):
    model = Torrent
    form_class = TorrentForm
    template_name = 'torrents/torrent_form.html'
    success_url = reverse_lazy('torrent_list')  # Redirect to torrent list after successful creation

    # Vérification : seul le propriétaire peut éditer le torrent
    # if torrent.user != request.user:
    #     return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce torrent.")
    
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

#
# Searh view
#

class TorrentSearchView(ListView):
    model = Torrent
    template_name = 'torrents/torrent_search.html'
    context_object_name = 'torrents'
    paginate_by = 40

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        sort_by = self.request.GET.get('sort_by', 'date')  # Default sorting by date
        torrents = Torrent.objects.filter(is_active=True)

        # Handle query validation
        if query:
            if len(query) < 2:  # Minimum 2-character search
                self.query_too_short = True
                return Torrent.objects.none()
            torrents = torrents.filter(name__icontains=query)
        else:
            self.query_too_short = False

        # Apply sorting logic
        if sort_by == 'seeds':
            torrents = torrents.order_by('-seed_count')
        elif sort_by == 'leeches':
            torrents = torrents.order_by('-leech_count')
        else:  # Default to date sorting
            torrents = torrents.order_by('-created_at')

        return torrents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '').strip()
        context['query'] = query
        context['result_count'] = self.get_queryset().count()
        context['query_too_short'] = getattr(self, 'query_too_short', False)
        context['sort_by'] = self.request.GET.get('sort_by', 'date')  # Pass the sorting method to the template
        return context
#
# Rewrite the access to .torrent
#

def serve_torrent_file(request, filename):
    try:
        # Find the torrent object by filename
        torrent = Torrent.objects.get(torrent_file__icontains=filename)

        # Serve the file using FileResponse, automatically handles file opening and closing
        return FileResponse(open(torrent.torrent_file.path, 'rb'), content_type='application/x-bittorrent')
    
    except Torrent.DoesNotExist:
        logger.error(f"Torrent with filename {filename} not found.")
        raise Http404("File not found.")
    except FileNotFoundError:
        logger.error(f"File for torrent {filename} does not exist on the server.")
        raise Http404("File not found.")
    except Exception as e:
        logger.error(f"Error serving torrent {filename}: {str(e)}")
        raise Http404("An unexpected error occurred.")

#
# Upload torrent views
#
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

                # Validate the saved torrent file
                absolute_torrent_file_path = os.path.join(settings.MEDIA_ROOT, metadata["torrent_file_path"])
                if not os.path.exists(absolute_torrent_file_path):
                    logger.error(f"Torrent file not found at: {absolute_torrent_file_path}")
                    messages.error(request, "Processed torrent file could not be found.")
                    return redirect('dashboard')

                # Create the Torrent instance
                with open(absolute_torrent_file_path, 'rb') as torrent_file:
                    torrent = create_torrent_instance(
                        metadata,
                        "",
                        File(torrent_file),
                        request.user
                    )

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
    """
    View to handle importing a torrent file from a URL by a logged-in user.
    """
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

                # Check for existing torrent with the same info_hash
                if Torrent.objects.filter(info_hash=info_hash).exists():
                    messages.info(request, f"The torrent with info_hash {info_hash} already exists in the database.")
                    logger.info(f"Torrent with info_hash {info_hash} already exists. Skipping import.")
                    return redirect('dashboard')

                # Determine save directory based on settings
                save_dir = determine_save_dir(info_hash, use_info_hash_folders)

                # Process the torrent file
                metadata = process_torrent_file(tmp_file_path, save_dir=save_dir)
                if not metadata:
                    messages.error(request, "Failed to process the torrent file.")
                    return redirect('dashboard')

                # Validate the saved torrent file
                absolute_path = os.path.join(settings.MEDIA_ROOT, metadata["torrent_file_path"])
                if not os.path.exists(absolute_path):
                    logger.error(f"Torrent file not found at: {absolute_path}")
                    messages.error(request, "Processed torrent file could not be found.")
                    return redirect('dashboard')

                # Create the Torrent instance
                with open(absolute_path, 'rb') as torrent_file:
                    torrent = create_torrent_instance(metadata, url, File(torrent_file), request.user)

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

    form = URLDownloadForm()
    return render(request, 'torrents/import_torrent_from_url.html', {'form': form})

