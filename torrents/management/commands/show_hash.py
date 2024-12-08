from django.core.management.base import BaseCommand
from torrents.models import Torrent

class Command(BaseCommand):
    help = "All info_hash in DB"


    def handle(self, *args, **kwargs):

        for i in Torrent.objects.all():
           print(i.info_hash)

           #self.stdout.write(absolute_path)
