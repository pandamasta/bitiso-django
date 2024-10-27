from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from torrents.models import Torrent, Project, Category
from django.contrib.auth.decorators import login_required

@login_required
def bulk_torrent_action(request):
    """
    Handle bulk actions on torrents, such as enabling, disabling, and updating categories or projects.
    """
    if request.method == 'POST':
        torrent_ids = request.POST.getlist('torrent_ids')
        action = request.POST.get('action')

        torrents = Torrent.objects.filter(id__in=torrent_ids)

        if action == 'enable':
            torrents.update(is_active=True)
        elif action == 'disable':
            torrents.update(is_active=False)
        elif action == 'update_category':
            category_id = request.POST.get('category')
            if category_id:
                category = Category.objects.get(id=category_id)
                torrents.update(category=category)
        elif action == 'update_project':
            project_id = request.POST.get('project')
            if project_id:
                project = Project.objects.get(id=project_id)
                torrents.update(project=project)

        messages.success(request, "Bulk action performed successfully.")
        return redirect('user_torrents')

    return redirect('user_torrents')
