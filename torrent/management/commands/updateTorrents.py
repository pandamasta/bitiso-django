from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from torrent.models import Torrent
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

        tracker_stats_file_current = os.path.join(settings.BITISO_TRACKER_STATS_FILES, 'tracker_stats_curent.txt')
        tracker_stats_file_last= os.path.join(settings.BITISO_TRACKER_STATS_FILES, 'tracker_stats_last.txt')

        try:
            # Get statistics page with seeders/leechers
            tracker_stats_live = urllib.request.urlopen(settings.BITISO_TRACKER_URL + settings.BITISO_TRACKER_STATS_PAGE)
            self.stdout.write(self.style.SUCCESS('Success during urlopen'))
        except:
            self.stdout.write(self.style.ERROR('Error during urlopen'))
            raise

        # Check if files stats exist

        if not os.path.exists(tracker_stats_file_current):
            print ('Create ' + tracker_stats_file_current)
            open(tracker_stats_file_current, 'a').close()

        if not os.path.exists(tracker_stats_file_last):
            print ('Create ' + tracker_stats_file_last)
            open(tracker_stats_file_last, 'a').close()

        # Move current stats file to last stat file

        print ('Copy previous stat from ' + tracker_stats_file_current + ' to ' + tracker_stats_file_last)
        shutil.copyfile(tracker_stats_file_current, tracker_stats_file_last)

        # Pull live tracker stats to file 

        print ('Insert tracker live stats to ' + tracker_stats_file_current)
        f1 = open(tracker_stats_file_current, 'w')
        f1.write(tracker_stats_live.read().decode('utf-8'))
        f1.close()

        # Files are differents (current vs previous)

        if not filecmp.cmp(tracker_stats_file_current, tracker_stats_file_last):
            print ("There is diff")

            with open(tracker_stats_file_current, 'r') as file1:
                with open(tracker_stats_file_last, 'r') as file2:
                    #same = set(file1).intersection(file2)
                    diff = set(file1).difference(file2)
            diff.discard('\n')

            # Update database with new leach and seed value
            for line in diff:
                line_split=line.rstrip("\n").split(':')
                print(line_split)

                q = Torrent.objects.get(hash=line_split[0].lower())
                q.seed = line_split[1]
                q.leech = line_split[2]
                q.save()

        else:
            print ("No diff")
