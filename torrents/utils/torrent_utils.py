import os
import logging
from torf import Torrent as Torrenttorf, BdecodeError, ReadError, WriteError
from django.conf import settings
from django.core.exceptions import ValidationError
from torrents.models import Torrent, Tracker

# Set up logging
logger = logging.getLogger(__name__)


def process_torrent_file(torrent_file_path, uploader, source_url=None, category=None, project=None):
    """
    Process and import a torrent file, add Bitiso trackers, and save the torrent to the database.
    
    Args:
        torrent_file_path: Path to the torrent file to be processed.
        uploader: The user who uploaded or triggered the import.
        source_url: Optional URL where the torrent was downloaded from.
        category: Optional Category object to assign to the torrent.
        project: Optional Project object to assign to the torrent.

    Returns:
        Torrent object if successfully processed, else None.
    """
    try:
        logger.info(f"Starting to process torrent file: {torrent_file_path}")

        # Read the torrent file
        t = Torrenttorf.read(torrent_file_path)
        logger.debug(f"Torrent {t.name} read successfully from {torrent_file_path}.")

        # Add Bitiso-specific tracker
        bitiso_trackers = [settings.TRACKER_ANNOUNCE]
        existing_trackers = [tracker for sublist in t.trackers for tracker in sublist]
        logger.debug(f"Existing trackers: {existing_trackers}")
        for tracker in bitiso_trackers:
            if tracker not in existing_trackers:
                t.trackers.append([tracker])
        logger.debug(f"Trackers after adding Bitiso: {t.trackers}")

        # Re-write the torrent file to a new path to avoid overwriting
        new_torrent_file_path = f"{os.path.splitext(torrent_file_path)[0]}_processed{os.path.splitext(torrent_file_path)[1]}"
        t.write(new_torrent_file_path)
        logger.info(f"Torrent file rewritten with Bitiso trackers at {new_torrent_file_path}.")

        # Check if the torrent already exists in the database by info_hash
        if Torrent.objects.filter(info_hash=t.infohash).exists():
            logger.warning(f"Torrent with info hash {t.infohash} already exists in the database. Skipping.")
            raise ValidationError(f"Torrent with info hash {t.infohash} already exists.")

        # Build the magnet URI and file list
        magnet_uri = str(t.magnet())
        file_list = ''.join([f"{file.name};{file.size}\n" for file in t.files])

        # Create Torrent object in the database
        torrent_obj = Torrent(
            info_hash=t.infohash[:40],  # Truncate for DB
            name=t.name[:128],  # Truncate for DB
            size=t.size,
            pieces=t.pieces,
            piece_size=t.piece_size,
            magnet=magnet_uri[:2048],
            torrent_filename=(t.name + '_processed.torrent')[:128],
            comment="Default comment"[:256],
            file_list=file_list[:2048],  # Truncate for DB
            file_count=len(t.files),
            category=category,
            project=project,
            user=uploader,
            is_bitiso=False,
            is_active=False,
            description="Default description"[:2000],
            website_url="",  # Empty by default
            website_url_download=source_url[:2000] if source_url else "",  # Download URL if provided
            website_url_repo="",  # Empty by default
            version="1.0"[:16],  # Default version
            seed_count=0,
            leech_count=0,
            download_count=0,
            completion_count=0
        )
        torrent_obj.save()
        logger.info(f"Torrent {torrent_obj.name} with hash {torrent_obj.info_hash} saved to the database.")

        # Process and link trackers
        _link_trackers_to_torrent(t, torrent_obj)

        return torrent_obj
    except (ReadError, WriteError, BdecodeError, FileNotFoundError, PermissionError) as e:
        logger.error(f"Error processing torrent file: {e}")
        raise ValidationError(f"Error processing torrent file: {e}")

def _link_trackers_to_torrent(t, torrent_obj):
    """
    Link the trackers found in the torrent to the database and the Torrent object.
    """
    list_of_tracker_ids = []
    for sublist in t.trackers:
        level = t.trackers.index(sublist)
        for tracker_url in sublist:
            tracker, created = Tracker.objects.get_or_create(url=tracker_url)
            list_of_tracker_ids.append([tracker.id, level])
            if created:
                logger.info(f"New tracker {tracker_url} added to the database.")
            else:
                logger.info(f"Existing tracker {tracker_url} found in the database.")

    # Link trackers to the Torrent object
    for tracker_id in list_of_tracker_ids:
        torrent_obj.trackers.add(tracker_id[0])
        tracker_stat = torrent_obj.trackerstat_set.get(tracker_id=tracker_id[0])
        tracker_stat.level = tracker_id[1]
        tracker_stat.save()
        logger.debug(f"Tracker {tracker_id[0]} linked to torrent {torrent_obj.name}.")