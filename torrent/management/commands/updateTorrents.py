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

    def add_arguments(self, parser):
        parser.add_argument("--full", help="Update all stats",
                            action="store_true")

        parser.add_argument("--diff", help="Update diff stats",
                            action="store_true")

    #def handle(self, *args, **options):
    def handle(self, *args, **kwargs):

        tracker_stats_file_current = os.path.join(settings.BITISO_TRACKER_STATS_FILES, 'tracker_stats_curent.txt')
        tracker_stats_file_last= os.path.join(settings.BITISO_TRACKER_STATS_FILES, 'tracker_stats_last.txt')

        # Get statistics page with seeders/leechers

        try:
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

#        print ('Copy previous stat from ' + tracker_stats_file_current + ' to ' + tracker_stats_file_last)
#        shutil.copyfile(tracker_stats_file_current, tracker_stats_file_last)

        # Pull live tracker stats to file 

        print ('Insert tracker live stats to ' + tracker_stats_file_current)
        f1 = open(tracker_stats_file_current, 'w')
        f1.write(tracker_stats_live.read().decode('utf-8'))
        f1.close()


        if kwargs['diff']:

        # Files are differents (current vs previous)

          if not filecmp.cmp(tracker_stats_file_current, tracker_stats_file_last):
              print ("There is diff")

              print ("Openfile file current and lasts")
              with open(tracker_stats_file_current, 'r') as file1:
                  with open(tracker_stats_file_last, 'r') as file2:
                      #same = set(file1).intersection(file2)
                      diff = set(file1).difference(file2)
              diff.discard('\n')

              # Update database with new leach and seed value
              for line in diff:
                  line_split=line.rstrip("\n").split(':')
                  print("Line split of diff " + str(line_split))

                  #q = Torrent.objects.get(info_hash=line_split[0].lower())
                  if Torrent.objects.filter(info_hash=line_split[0].lowser()).exists():
                    print("Info hash " + line_split[0].lower() + "exist, Update value")
                    q = Torrent.objects.get(info_hash=line_split[0].lower())
                    q.seed = line_split[1]
                    q.leech = line_split[2]
                    q.save()
                  else:
                     print("Info hash " + line_split[0].lower() + "doesnt't exist. Skip")


              shutil.move(tracker_stats_file_current, tracker_stats_file_last)


          else:
              print ("No diff")


        # Update all torrents stats in DB
        if kwargs['full']:

          print ('Update all torrent stats')
          with open(tracker_stats_file_current) as file:
              for line in file:
                  line_split=line.rstrip().split(':')
                  info_hash_lower=line_split[0].lower()
                  seed=line_split[1]
                  leech=line_split[2]
                  
                  if Torrent.objects.filter(info_hash=info_hash_lower).exists():
                    print("Update stats for: " + info_hash_lower + " " + seed + " " + leech)
                    q = Torrent.objects.get(info_hash=info_hash_lower)
                    q.seed = seed
                    q.leech = leech
                    q.save()
                  else:
                    print("Not in DB: " + info_hash_lower)
