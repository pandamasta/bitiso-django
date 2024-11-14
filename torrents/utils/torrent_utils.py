import os
import logging
from torf import Torrent as Torrenttorf, BdecodeError, ReadError, WriteError
from django.conf import settings
from django.core.exceptions import ValidationError
from torrents.models import Torrent, Tracker
from torrents.models import Tracker, TrackerStat
from django.utils.text import slugify
import requests
from urllib.parse import urlparse
import tempfile  
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)


def extract_info_hash(torrent_file_path):
    """Extracts the info_hash from a torrent file."""
    try:
        t = Torrenttorf.read(torrent_file_path)
        return t.infohash
    except Exception as e:
        logger.error(f"Error extracting info_hash from torrent file: {e}")
        return None


def download_torrent(url):
    """Download torrent file from an URL and return temp file """
    try:
        response = requests.get(url)
        response.raise_for_status()
        original_filename = os.path.basename(urlparse(url).path) or "downloaded_torrent"
        tmp_file_path = os.path.join(tempfile.gettempdir(), f"{original_filename}_temp.torrent")
        with open(tmp_file_path, 'wb') as tmp_file:
            tmp_file.write(response.content)
        return tmp_file_path
    except requests.RequestException as e:
        logger.error(f"Error downloading torrent from {url}: {e}")
        return None


def determine_save_dir(info_hash, use_info_hash_folders):
    """Determines the directory for saving torrent files."""
    if use_info_hash_folders:
        subdir_1, subdir_2 = info_hash[:2], info_hash[2:4]
        torrent_dir = os.path.join(settings.MEDIA_TORRENT, subdir_1, subdir_2)
    else:
        torrent_dir = settings.MEDIA_TORRENT
    os.makedirs(os.path.join(settings.MEDIA_ROOT, torrent_dir), exist_ok=True)
    return torrent_dir


def create_torrent_instance(metadata, url, torrent_file, user):
    """Creates and saves a Torrent instance in the database."""
    torrent = Torrent(
        info_hash=metadata["info_hash"],
        name=metadata["name"],
        slug=slugify(metadata["name"]),
        torrent_file=torrent_file,
        website_url_download=url,
        user=user,
        size=metadata["size"],
        pieces=metadata["pieces"],
        piece_size=metadata["piece_size"],
        magnet=metadata["magnet"],
        file_list=metadata["file_list"],
        file_count=metadata["file_count"]
    )
    torrent.save()
    return torrent


def _link_trackers_to_torrent(trackers, torrent_obj):
    """Link each tracker URL to the Torrent object and set announce_priority."""
    for level, tracker_list in enumerate(trackers):
        for tracker_url in tracker_list:
            if tracker_url:
                try:
                    # Get or create the tracker by URL
                    tracker, created = Tracker.objects.get_or_create(url=tracker_url)
                    torrent_obj.trackers.add(tracker)
                    
                    # Set announce_priority directly for each tracker in TrackerStat
                    tracker_stat, _ = torrent_obj.trackerstat_set.get_or_create(
                        tracker=tracker,
                        defaults={'announce_priority': level}
                    )
                    tracker_stat.announce_priority = level
                    tracker_stat.save()
                    logger.debug(f"Linked tracker {tracker_url} to torrent {torrent_obj.name} with announce_priority {level}")
                
                except Exception as e:
                    logger.error(f"Failed to link tracker {tracker_url} to torrent {torrent_obj.name}: {e}")


def process_torrent_file(torrent_file_path, save_dir):
    """Processes the torrent file, adding custom trackers, and saves it."""
    try:
        logger.info(f"Processing torrent file: {torrent_file_path}")
        t = Torrenttorf.read(torrent_file_path)
        logger.info(f"Parsed torrent file: {t.name}")

        # Add custom tracker if not present
        custom_tracker = settings.TRACKER_ANNOUNCE
        if custom_tracker not in {tracker for sublist in t.trackers for tracker in sublist}:
            t.trackers.append([custom_tracker])
            logger.info(f"Added custom tracker: {custom_tracker}")

        # Define the save path using the save directory and name
        save_path = os.path.join(save_dir, f"{t.name}.torrent")
        
        # Check for an existing file and a corresponding instance
        if os.path.exists(save_path):
            logger.info(f"File already exists at: {save_path}. Checking for corresponding database entry.")
            if Torrent.objects.filter(info_hash=t.infohash).exists():
                # If instance exists, skip saving as the torrent is fully imported
                logger.info(f"Torrent with info_hash {t.infohash} already exists. Skipping save.")
                return None
            else:
                # If instance doesn't exist, assume incomplete import and delete the existing file
                logger.info(f"No database entry found for {t.infohash}. Deleting incomplete file at {save_path}.")
                os.remove(save_path)

        # Save the modified torrent file with custom trackers
        t.write(save_path)
        logger.info(f"Processed torrent file saved at: {save_path}")

        # Return metadata with relative path for DB
        return {
            "info_hash": t.infohash,
            "name": t.name[:128],
            "size": t.size,
            "pieces": t.pieces,
            "piece_size": t.piece_size,
            "magnet": str(t.magnet()),
            "torrent_file_path": os.path.relpath(save_path, settings.MEDIA_ROOT),
            "file_list": [{"name": file.name, "size": file.size} for file in t.files],
            "file_count": len(t.files),
            "trackers": t.trackers
        }
    except Exception as e:
        logger.error(f"Error processing torrent file: {e}")
        return None
