from django.core.management.base import BaseCommand
from django.conf import settings
import os
from torf import Torrent as Torrenttorf
from torrent.models import Torrent, Tracker
import shutil
import re


class Command(BaseCommand):
    help = "Import torrent from existing one"

    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-p', '--path', type=str, help='Define path of data to be created as torrent', )

    def handle(self, *args, **kwargs):

        t = Torrenttorf.read

        torrent_file_tmp = settings.TORRENT_FILES_TMP

        for i in os.listdir(torrent_file_tmp):
            absolute_path = os.path.join(torrent_file_tmp, i)
            print("Read Torrent: " + absolute_path)

            # Read meta info from .torrent

            t = Torrenttorf.read(absolute_path)

            # Check if info_hash exit in DB

            # if Torrent.objects.filter(info_hash=t.infohash).exists():
            #     print("Info hash " + t.infohash + " already exist in DB. skip")
            #     continue

            # Insert bitiso tracker

            print("Insert bitiso tracker")
            print("Current Trackers in the torrent")
            print(t.trackers)
            print("Insert tracker from settings.TRACKER_ANNOUNCE ")
            t.trackers.insert(1, settings.TRACKER_ANNOUNCE)
            print("Tracker list after insert: " + str(t.trackers))

            # Write the .torrent

            # print("Write torrent to:" + os.path.join(settings.TORRENT_FILES, t.name + '.torrent'))
            # t.write(os.path.join(settings.TORRENT_FILES, t.name + '.torrent'))

            # Insert unknown tracker in DB

            list_of_tracker_id = []
            print("Insert unknown tracker in DB")
            for sublist in t.trackers:
                level = t.trackers.index(sublist)
                for tracker_url in sublist:
                    print("tracker_url : " + str(tracker_url) + "level: " + str(level))
                    if not Tracker.objects.filter(url=tracker_url).exists():
                        print('Insert new tracker: ' + str(tracker_url))
                        tracker = Tracker(url=tracker_url)
                        tracker.save()
                        list_of_tracker_id.append([tracker.id,level])
                    else:
                        list_of_tracker_id.append([Tracker.objects.get(url=tracker_url).id, level])

                    print(list_of_tracker_id)

            # Insert torrent metadata in DB

            file_list = ''
            for file in t.files:
                file_list += str(file.name + ';' + str(file.size) + '\n')
            print("File in torrent: " + file_list)
            obj = Torrent(info_hash=t.infohash, name=t.name, size=t.size, pieces=t.pieces, piece_size=t.piece_size,
                          magnet=t.magnet(), torrent_filename=t.name + '.torrent',
                          metainfo_file='torrent/' + t.name + '.torrent', file_list=file_list, file_nbr=len(t.files))
            obj.save()


            # Attach tracker to torrent and set the tracker level

            for tracker_id in list_of_tracker_id:
                obj.trackers.add(tracker_id[0])
                # obj.save()
                t=obj.trackerstat_set.get(tracker_id=tracker_id[0])
                t.level=tracker_id[1]
                t.save()

            # for tracker_local_id in settings.TRACKER_ANNOUNCE:
            #     if not Tracker.objects.filter(url=tracker_local_id).exists():
            #         obj.trackers.add(Tracker.objects.filter(url=tracker_local_id).id())

# #           # Move data to torrent client path
# #
# #
#            # absolute path
#            src_path = absolute_path
#            dst_path = settings.TORRENT_FILES_TMP_OK
#
#            print ("Move file " + src_path)
#            print ("To :" + dst_path)
#
#            shutil.move(src_path, dst_path + '/' + t.name  + '.torrent')
#
#            #self.stdout.write(absolute_path)
