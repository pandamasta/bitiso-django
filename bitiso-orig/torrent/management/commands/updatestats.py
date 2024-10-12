from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from torrent.models import Torrent

import os, shutil, filecmp, urllib.request
from pathlib import Path

tracker_stats_live = urllib.request.urlopen(settings.TRACKER_URL + settings.TRACKER_STATS)

class Command(BaseCommand):
    help = "Update seed and leech stats in DB"


    def handle(self, *args, **kwargs):

        # Get statistics page with seeders/leechers
        try:
            tracker_stats_live = urllib.request.urlopen(settings.TRACKER_URL + settings.TRACKER_STATS)
            self.stdout.write(self.style.SUCCESS('Success during urlopen'))
        except:
            self.stdout.write(self.style.ERROR('Error during urlopen'))
            raise

        data=tracker_stats_live.read()

        for t in data.split():
            print(t.decode().split(':'))
            line=t.decode().split(':')

            ##q = Torrent.objects.get(info_hash=line_split[0].lower())
            if Torrent.objects.filter(info_hash=line[0].lower()).exists():
              print("Info hash " + line[0].lower() + "exist, Update value")
              q = Torrent.objects.get(info_hash=line[0].lower())
              q.seed = line[1]
              q.leech = line[2]
              q.save()
            else:
               print("Info hash " + line[0].lower() + "doesnt't exist. Skip")
