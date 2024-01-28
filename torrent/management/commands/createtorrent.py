from django.core.management.base import BaseCommand
from django.conf import settings
import os
from torf import Torrent as Torrenttorf
from torrent.models import Torrent, Tracker
import shutil
import datetime
import re
import hashlib

class Command(BaseCommand):
    help = "Create torrents (metainfo files) for files and directories in TORRENT_DATA_TMP"

    def create_torrent_and_move(self, file_path):
        # Check if the file is empty
        if os.stat(file_path).st_size == 0:
            print("File: {} is empty. Skip".format(file_path))
            return

        # Check if the torrent file already exists
        torrent_filename = os.path.basename(file_path) + ".torrent"
        absolute_path_torrent = os.path.join(settings.BITISO_TORRENT_STATIC, torrent_filename)
        if os.path.isfile(absolute_path_torrent):
            print("File: {} already exists. Skip".format(absolute_path_torrent))
            return

        # Calculate the SHA-256 hash of the file
        sha256_hash_value = hashlib.sha256()
        # Calcul du hachage SHA-256 du fichier
        sha256_hash_value = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash_value.update(byte_block)
        hash_signature = sha256_hash_value.hexdigest()

        print("File hash {}: {}".format(file_path, hash_signature))

        # Create the metainfo file (.torrent)
        now = datetime.datetime.now()
        t = Torrenttorf(
            file_path,
            trackers=settings.TRACKER_ANNOUNCE,
            comment='',
            created_by='Bitiso.org',
            creation_date=now
        )
        t.private = True
        t.generate()

        # Check if infohash exists in the database
        if Torrent.objects.filter(info_hash=t.infohash).exists():
            print("Info hash {} already exists in DB".format(t.infohash))
            return

        if not os.path.exists(settings.TORRENT_FILES):
            os.makedirs(settings.TORRENT_FILES)

        # Path to the torrent file
        torrent_file_path = os.path.join(settings.TORRENT_FILES, t.name + '.torrent')

        # Check if the torrent file already exists
        if os.path.isfile(torrent_file_path):
            print("The torrent file already exists and will be replaced: {}".format(torrent_file_path))
            os.remove(torrent_file_path)

        t.write(torrent_file_path)
        print("Write torrent: {}".format(t.name + '.torrent'))

        # Insert unknown trackers into the database
        list_of_tracker_id = []
        for tracker_url in t.trackers:
            tracker_url_sanitized = re.search('\'(.*)\'', str(tracker_url), re.IGNORECASE).group(1)
            if not Tracker.objects.filter(url=tracker_url_sanitized).exists():
                print('Insert new tracker: {}'.format(tracker_url_sanitized))
                tracker = Tracker(url=tracker_url_sanitized)
                tracker.save()
                list_of_tracker_id.append(tracker.id)
            list_of_tracker_id.append(Tracker.objects.get(url=tracker_url_sanitized).id)
        print(list_of_tracker_id)

        # Format file list
        file_list = ''
        for i in t.files:
            file_list += '{};{}\n'.format(i.name, i.size)

        # Insert general metadata into the database
        obj = Torrent(
            info_hash=t.infohash,
            name=t.name,
            size=t.size,
            pieces=t.pieces,
            piece_size=t.piece_size,
            magnet=t.magnet(),
            torrent_filename=t.name + '.torrent',
            metainfo_file='torrent/' + t.name + '.torrent',
            file_list=file_list,
            file_nbr=len(t.files),
            hash_signature=hash_signature
        )
        obj.save()

        for tracker_id in list_of_tracker_id:
            obj.trackers.add(tracker_id)

        # Move data to the torrent client path
        src_path = os.path.dirname(file_path)
        dst_path = settings.TORRENT_DATA

        print("Moving file {} to: {}".format(file_path, dst_path))
        shutil.move(file_path, dst_path)

    def create_torrent_for_directory_and_move(self, dir_path, hash_signature):

        print("Creating torrent for directory: {}".format(dir_path))

        # Check if the directory is empty
        if not os.listdir(dir_path):
            print("Directory: {} is empty. Skip".format(dir_path))
            return

        # Create a torrent for the entire directory
        dir_name = os.path.basename(dir_path)
        torrent_dir_path = os.path.join(settings.TORRENT_DATA_TMP, dir_name + '.torrent')

        # Check if the torrent file already exists
        if os.path.isfile(torrent_dir_path):
            print("The torrent file for the directory already exists: {}. Skip".format(torrent_dir_path))
            return

        t = Torrenttorf(
            dir_path,
            trackers=settings.TRACKER_ANNOUNCE,
            comment='',
            created_by='Bitiso.org',
            creation_date=datetime.datetime.now()
        )
        t.private = True
        t.generate()

        # Check if infohash exists in the database
        if Torrent.objects.filter(info_hash=t.infohash).exists():
            print("Info hash {} already exists in DB".format(t.infohash))
            return

        # Path to the torrent file for the directory
        torrent_file_path = os.path.join(settings.TORRENT_FILES, dir_name + '.torrent')

        # Check if the torrent file already exists
        if os.path.isfile(torrent_file_path):
            print(
                "The torrent file for the directory already exists and will be replaced: {}".format(torrent_file_path))
            os.remove(torrent_file_path)

        t.write(torrent_file_path)
        print("Write torrent for directory: {}".format(t.name + '.torrent'))

        # Insert unknown trackers into the database
        list_of_tracker_id = []
        for tracker_url in t.trackers:
            tracker_url_sanitized = re.search('\'(.*)\'', str(tracker_url), re.IGNORECASE).group(1)
            if not Tracker.objects.filter(url=tracker_url_sanitized).exists():
                print('Insert new tracker: {}'.format(tracker_url_sanitized))
                tracker = Tracker(url=tracker_url_sanitized)
                tracker.save()
                list_of_tracker_id.append(tracker.id)
            list_of_tracker_id.append(Tracker.objects.get(url=tracker_url_sanitized).id)
        print(list_of_tracker_id)

        # Format file list
        file_list = ''
        for i in t.files:
            file_list += '{};{}\n'.format(i.name, i.size)

        # Insert general metadata into the database
        obj = Torrent(
            info_hash=t.infohash,
            name=t.name,
            size=t.size,
            pieces=t.pieces,
            piece_size=t.piece_size,
            magnet=t.magnet(),
            torrent_filename=t.name + '.torrent',
            metainfo_file='torrent/' + t.name + '.torrent',
            file_list=file_list,
            file_nbr=len(t.files),
            hash_signature=hashlib.sha256()
        )
        obj.save()

        for tracker_id in list_of_tracker_id:
            obj.trackers.add(tracker_id)

    def handle(self, *args, **kwargs):
        # Get the path from the command line arguments or use the default
        torrent_data = kwargs.get('path') or settings.TORRENT_DATA_TMP

        # Check if the path is defined
        if not torrent_data:
            print("The path to the torrent folder is not defined.")
            return

        enforce_create = settings.ENFORCE_CREATE

        # Check if the directory exists and create it if necessary
        if not os.path.exists(torrent_data):
            if enforce_create:
                os.makedirs(torrent_data)
            else:
                print("The directory does not exist: {} and ENFORCE_CREATE is disabled.".format(torrent_data))
                return

        # Process files and directories
        for item in os.listdir(torrent_data):
            item_path = os.path.join(torrent_data, item)

            # Check if it's a file
            if os.path.isfile(item_path):
                self.create_torrent_and_move(item_path)

            # Check if it's a directory
            if os.path.isdir(item_path):
                hash_signature = hashlib.sha256()  # Calcul du hachage SHA-256
                self.create_torrent_for_directory_and_move(item_path, hash_signature)