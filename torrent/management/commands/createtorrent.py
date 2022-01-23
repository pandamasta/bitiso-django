from django.core.management.base import BaseCommand
from django.conf import settings
import os
from torf import Torrent as Torrenttorf
from torrent.models import Torrent
import shutil

class Command(BaseCommand):
    help = "Create a torrent aka metainfo file from file or direcotry"
    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-p', '--path', type=str, help='Define path of data to be created as torrent', )

    def handle(self, *args, **kwargs):

        #torrent_data=settings.TORRENT_DATA
        #torrent_files=settings.TORRENT_FILES
        

        for i in os.listdir(settings.TORRENT_DATA_TMP):
           absolute_path = os.path.join(settings.TORRENT_DATA_TMP,i)

           ## Create the metainfo file .torrent

           t = Torrenttorf(absolute_path, 
                       trackers=['http://tracker.bitiso.net:6969/announce'],
                       comment='Torrent created by bitiso.org')

           t.private = True
           t.generate()

           t.write(os.path.join(settings.TORRENT_FILES,t.name+'.torrent'))


           # Insert general metadata in DB

           obj = Torrent(hash=t.infohash, name=t.name, size=t.size, pieces=t.pieces, piece_size=t.piece_size, magnet=t.magnet(),torrent_filename=t.name + '.torrent',metainfo_file='torrent/'+ t.name + '.torrent')
           
           obj.save()

           # Move data to torrent client path


           # absolute path
           src_path = absolute_path
           dst_path = settings.TORRENT_DATA + '/' + i

           print (src_path)
           print (dst_path)
           shutil.move(src_path, dst_path)

           self.stdout.write(absolute_path)

        #path = kwargs['path']

