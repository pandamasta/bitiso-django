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

        #torrent_data=settings.TORRENT_DATA
        #torrent_files=settings.TORRENT_FILES
        
        t = Torrenttorf.read

        torrent_file_tmp=settings.TORRENT_FILES_TMP

        for i in os.listdir(torrent_file_tmp):
           absolute_path = os.path.join(torrent_file_tmp,i)

           ## Read meta info from .torrent

           t = Torrenttorf.read(absolute_path)

           # Check if infohash exit in DB

           if Torrent.objects.filter(info_hash=t.infohash).exists():
             print("Info hash " + t.infohash + " already exist in DB. skip")
             continue

           # Insert bitiso tracker

           t.trackers.insert(0,'http://tracker.bitiso.org:6969/announce')


           # Write the .torrent

           t.write(os.path.join(settings.TORRENT_FILES,t.name+'.torrent'))

           # Insert unknown tracker in DB

           list_of_tracker_id=[]
           for tracker_url in t.trackers:

             tracker_url_sanitized=re.search('\'(.*)\'', str(tracker_url), re.IGNORECASE).group(1)

             if not Tracker.objects.filter(url=tracker_url_sanitized).exists():

                print('Insert new tracker: '+ str(tracker_url_sanitized))
                tracker=Tracker(url=tracker_url_sanitized)
                tracker.save()
                list_of_tracker_id.append(tracker.id)

             list_of_tracker_id.append(Tracker.objects.get(url=tracker_url_sanitized).id)
           print(list_of_tracker_id)
              
         

           # Insert general metadata in DB

           file_list=''
           for i in t.files:
               file_list+=str(i.name + ';' +  str(i.size) + '\n')
               print(file_list)

           obj = Torrent(info_hash=t.infohash, name=t.name, size=t.size, pieces=t.pieces, piece_size=t.piece_size, magnet=t.magnet(),torrent_filename=t.name + '.torrent',metainfo_file='torrent/'+ t.name + '.torrent', file_list=file_list, file_nbr=len(t.files))

#           
           obj.save()

           for tracker_id in list_of_tracker_id:
             obj.trackers.add(tracker_id)
#
#           # Move data to torrent client path
#
#
           # absolute path
           src_path = absolute_path
           dst_path = settings.TORRENT_FILES_TMP_OK

           print ("Move file " + src_path)
           print ("To :" + dst_path)

           shutil.move(src_path, dst_path + '/' + t.name  + '.torrent')

           #self.stdout.write(absolute_path)
