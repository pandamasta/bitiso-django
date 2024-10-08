# views/dashboard_views.py
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Torrent, Category, Project
from ..forms import FileUploadForm, URLDownloadForm
from ..services.torrent_service import TorrentService
from django.conf import settings

# For all actions related to the user's personal dashboard (managing torrents, viewing stats, etc.).

@login_required
# def dashboard(request):
#     # Fetch user-specific torrent management data
#     torrents = Torrent.objects.filter(uploader=request.user).order_by('-creation')
#     return render(request, 'user/dashboard.html', {'torrents': torrents})

def dashboard(request):
    user_torrents = Torrent.objects.filter(uploader=request.user).order_by('-creation')
    torrent_count = user_torrents.count()
    categories = Category.objects.all()
    projects = Project.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        torrent_ids = request.POST.getlist('torrent_ids')

        if action == 'delete':
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
            messages.success(request, "Selected torrents have been deleted.")
        elif action == 'activate':
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=True)
            messages.success(request, "Selected torrents have been activated.")
        elif action == 'deactivate':
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=False)
            messages.success(request, "Selected torrents have been deactivated.")
        elif action == 'set_category':
            category_id = request.POST.get('category_id')
            if category_id:
                category = Category.objects.get(id=category_id)
                Torrent.objects.filter(id__in=torrent_ids).update(category=category)
                messages.success(request, "Category updated successfully.")
        elif action == 'set_project':
            project_id = request.POST.get('project_id')
            if project_id:
                project = Project.objects.get(id=project_id)
                Torrent.objects.filter(id__in=torrent_ids).update(project=project)
                messages.success(request, "Project updated successfully.")
        return redirect('bitiso:manage_dashboard')

    form = FileUploadForm()
    url_form = URLDownloadForm()

    return render(request, 'user/dashboard.html', {
        'torrents': user_torrents,
        'torrent_count': torrent_count,
        'form': form,
        'url_form': url_form,
        'categories': categories,
        'projects': projects
    })

@login_required
def delete_torrents(request):
    if request.method == 'POST':
        torrent_ids = request.POST.getlist('torrent_ids')
        if torrent_ids:
            Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
            messages.success(request, "Selected torrents have been deleted.")
        else:
            messages.warning(request, "No torrents were selected for deletion.")
    return redirect('dashboard')
# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)

# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)


# Assurez-vous que le répertoire settings.MEDIA_TORRENT existe
os.makedirs(settings.MEDIA_TORRENT, exist_ok=True)