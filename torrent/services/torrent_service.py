# services/torrent_service.py

from ..models import Torrent, Tracker, TrackerStat
from django.conf import settings
from torf import Torrent as TorrentTorf, BdecodeError, ReadError, WriteError
import os

class TorrentService:
    def handle_uploaded_file(self, file, user):
        """
        Handle the uploaded torrent file.
        """
        try:
            t = TorrentTorf.read(file)
        except (ReadError, BdecodeError) as e:
            raise ValueError("Invalid torrent file format.") from e

        if Torrent.objects.filter(info_hash=t.infohash).exists():
            raise ValueError(f"Torrent with hash {t.infohash} already exists.")

        # Process file list
        file_list = '\n'.join([f"{f.name};{f.size}" for f in t.files])
        
        # Create Torrent object
        torrent = Torrent.objects.create(
            info_hash=t.infohash[:40],
            name=t.name[:128],
            size=t.size,
            pieces=t.pieces,
            piece_size=t.piece_size,
            magnet=str(t.magnet())[:2048],
            torrent_filename=(t.name + '.torrent')[:128],
            comment="Default comment"[:256],
            file_list=file_list[:2048],
            file_nbr=len(t.files),
            uploader=user,
            description="Default description"[:2000],
            website_url="",
            website_url_download="",
            website_url_repo="",
            version="1.0"[:16],
            hash_signature=""[:128],
            is_active=False,
            is_bitiso=False,
            category=None,
            project=None
        )

        # Handle trackers
        self._add_trackers(torrent, t.trackers)

        # Save metainfo_file if needed
        # Assuming 'file' is the path to the uploaded file
        # You might need to adjust this based on how you handle file uploads
        torrent.metainfo_file.save(os.path.basename(file), file)

        return torrent

    def _add_trackers(self, torrent, tracker_lists):
        """
        Add trackers to a torrent.
        """
        for level, trackers in enumerate(tracker_lists):
            for tracker_url in trackers:
                tracker, created = Tracker.objects.get_or_create(url=tracker_url)
                torrent.trackers.add(tracker)
                # Create TrackerStat
                TrackerStat.objects.create(
                    torrent=torrent,
                    tracker=tracker,
                    level=level,
                    seed=0,
                    leech=0,
                    complete=0
                )
