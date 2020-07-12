from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from torrent.models import *
import os, shutil, filecmp, urllib.request
from pathlib import Path

class Command(BaseCommand):
    help = 'Update statistics for all torrent from tracker'
    '''
    def add_arguments(self, parser):
        parser.add_argument('--torrent_id',
                            action='store_true',
                            nargs='+', type=int)
    '''
    def handle(self, *args, **options):
        pathFileTrackerStatsDL = os.path.join(settings.TORRENT_ROOT_TMP, 'trackerStats.txt')
        pathFileTrackerStatsDLPrev = os.path.join(settings.TORRENT_ROOT_TMP, 'trackerStats_prev.txt')

        try:
            # Check statistics page with seeders/leechers
            trackerStats = urllib.request.urlopen(settings.BITISO_TRACKER_URL + settings.BITISO_TRACKER_STATS_PAGE)
            self.stdout.write(self.style.SUCCESS('Success during urlopen'))
        except:
            self.stdout.write(self.style.ERROR('Error during urlopen'))
            raise

        # Copy previous statistics page if exist
        if Path(pathFileTrackerStatsDL).is_file():
            shutil.copyfile(pathFileTrackerStatsDL, pathFileTrackerStatsDLPrev)

        trackerStatsSL = open(pathFileTrackerStatsDL, 'w')
        trackerStatsSL.write(trackerStats.read().decode('utf-8'))
        trackerStatsSL.close()

        # Files are differents (current vs previous)
        if Path(pathFileTrackerStatsDLPrev).is_file() and not filecmp.cmp(pathFileTrackerStatsDL, pathFileTrackerStatsDLPrev):
            TorrentStatSL.objects.all().delete()
            trackerStatsSL = open(pathFileTrackerStatsDL, 'r')

            torrentStat = TorrentStatSL()
            # Update
            for trackerStatLine in trackerStatsSL.readlines():
                torrentInfos = trackerStatLine.split(':')
                torrentStat.hash = torrentInfos[0]
                torrentStat.seederNr = torrentInfos[1]
                torrentStat.leecherNr = torrentInfos[2]

                try:
                    torrentStat.save()
                except:
                    pass

            trackerStatsSL.close()

            try:
                Torrent.objects.raw('UPDATE torrent_Torrent AS t ' +
                                    'SET seed = tsl.seederNr, leech = tsl.leecherNr ' +
                                    'FROM torrent_TorrentStatSL AS tsl ' +
                                    'WHERE t.hash = tsl.hash;')
                self.stdout.write(self.style.SUCCESS('Successfully update torrent statistics!'))
            except:
                self.stdout.write(self.style.ERROR('Error during update torrent statistics!'))
