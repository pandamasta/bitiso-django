from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from torrents.models import Torrent
from django.contrib.auth.decorators import login_required

@login_required
def bulk_torrent_action(request):
    if request.method == "POST":
        action = request.POST.get("action")  # Get the action (enable/disable)
        torrent_ids = request.POST.getlist("torrent_ids")  # Get the list of selected torrent IDs

        if not torrent_ids:
            messages.error(request, "No torrents were selected.")
            return redirect('user_torrents')

        torrents = Torrent.objects.filter(id__in=torrent_ids, user=request.user)  # Ensure ownership

        if action == "enable":
            torrents.update(is_active=True)
            messages.success(request, f"{torrents.count()} torrents have been enabled.")
        elif action == "disable":
            torrents.update(is_active=False)
            messages.success(request, f"{torrents.count()} torrents have been disabled.")
        else:
            messages.error(request, "Invalid action.")
        
        return redirect('user_torrents')
