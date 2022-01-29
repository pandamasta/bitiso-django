from django.core.management.base import BaseCommand
from django.conf import settings
import os
from torf import Torrent as Torrenttorf
from torrent.models import Torrent
import shutil

class Command(BaseCommand):
    help = "All info_hash in DB"


    def handle(self, *args, **kwargs):

        for i in Torrent.objects.all():
           print(i.info_hash)

           #self.stdout.write(absolute_path)


