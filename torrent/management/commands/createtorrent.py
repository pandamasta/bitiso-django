from django.core.management.base import BaseCommand
from django.conf import settings
import os
from torf import Torrent as Torrenttorf
from torrent.models import Torrent, Tracker
import shutil
import datetime
import re
import hashlib
from django.conf import settings

class Command(BaseCommand):
    help = "Create a torrent (metainfo file) from a file or a directory"
    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-p', '--path', type=str, help='Define path of data to be created as torrent', )


    def handle(self, *args, **kwargs):

        torrent_data=settings.TORRENT_DATA_TMP
        #torrent_data=settings.TORRENT_DATA

        for i in os.listdir(torrent_data):
           absolute_path = os.path.join(torrent_data,i)
           torrent_filename = i+".torrent"
           absolute_path_torrent = settings.TORRENT_FILES + '/' + torrent_filename 

           # Check if file not null, not existing, and not a directory

           if os.stat(absolute_path).st_size == 0:
             print("File: " + absolute_path + " is empty. Skip")
             continue

           if os.path.isfile(absolute_path_torrent):
             print("File: " + os.path.join(absolute_path_torrent + ' already exist. Skip' ))
             continue

           if os.path.isdir(absolute_path):
             print("File: " + absolute_path + " is a directory. Skip")
             continue

           # Hash 256
 
           sha256_hash = hashlib.sha256()
           with open(absolute_path,"rb") as f:
               # Read and update hash string value in blocks of 4K
               for byte_block in iter(lambda: f.read(4096),b""):
                   sha256_hash.update(byte_block)
               sha256=sha256_hash.hexdigest()

           print("File hash " + absolute_path + " " + sha256)

           ## Create the metainfo file .torrent

           now = datetime.datetime.now()

           t = Torrenttorf(absolute_path, 
                       trackers=[settings.TRACKER_ANNOUNCE],
                       comment='',
                       created_by='Bitiso.org',
                       creation_date=now)


           t.private = True
           t.generate()


           # Check if infohash exit in DB

           if Torrent.objects.filter(info_hash=t.infohash).exists():
             print("Info hash " + t.infohash + " already exist in DB")
             continue


           t.write(os.path.join(settings.TORRENT_FILES,t.name+'.torrent'))
           print("Write torrent: " + t.name+'.torrent')


           # Insert unknown tracker in DB

           list_of_tracker_id=[]
           print(t.trackers)
           for tracker_url in t.trackers:

             tracker_url_sanitized=re.search('\'(.*)\'', str(tracker_url), re.IGNORECASE).group(1)

             if not Tracker.objects.filter(url=tracker_url_sanitized).exists():

                print('Insert new tracker: '+ str(tracker_url_sanitized))
                tracker=Tracker(url=tracker_url_sanitized)
                tracker.save()
                list_of_tracker_id.append(tracker.id)

             list_of_tracker_id.append(Tracker.objects.get(url=tracker_url_sanitized).id)
           print(list_of_tracker_id)

           # Format file list
           file_list=''
           for i in t.files:
               file_list+=str(i.name + ';' +  str(i.size) + '\n')
               print(file_list)

           # Insert general metadata in DB
           obj = Torrent(info_hash=t.infohash, name=t.name, size=t.size, pieces=t.pieces, piece_size=t.piece_size, magnet=t.magnet(),torrent_filename=t.name + '.torrent',metainfo_file='torrent/'+ t.name + '.torrent', file_list=file_list, file_nbr=len(t.files), hash_signature=sha256)
           
           obj.save()

           for tracker_id in list_of_tracker_id:
             obj.trackers.add(tracker_id)

           # Move data to torrent client path

           # absolute path
           src_path = absolute_path
           dst_path = settings.TORRENT_DATA + "/" 

           print ("Move file " + src_path)
           print ("To :" + dst_path)

           shutil.move(src_path, dst_path)


           #self.stdout.write(absolute_path)

        #path = kwargs['path']

