from django.core.management.base import BaseCommand
from torrents.models import Torrent

class Command(BaseCommand):
    help = "Calculate and print the total size of all torrents in MB"

    def handle(self, *args, **kwargs):
        total_size_bytes = 0

        # Iterate through all Torrent objects and sum up the sizes
        for torrent in Torrent.objects.all():
            total_size_bytes += torrent.size
        
        # Convert total size to MB (1 MB = 1024 * 1024 bytes)
        total_size_mb = total_size_bytes / (1024 ** 2)

        # Print the total size in MB
        print(f"Total size: {total_size_mb:.2f} MB")