from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Torrent

@receiver([post_save, post_delete], sender=Torrent)
def update_torrent_count(sender, instance, **kwargs):
    """
    Updates the torrent_count field on the related project.
    Triggered when a torrent is added or deleted.
    """
    project = instance.project
    project.torrent_count = project.torrents.count()  # Count related torrents
    project.save()
