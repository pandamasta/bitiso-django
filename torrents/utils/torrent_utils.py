# torrents/utils/torents_utils.py

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
        logger.error(f"Error extracting info_hash from file {torrent_file_path}: {e}")
        return None


def download_torrent(url):
    """Download torrent file from a URL and return its temporary file path."""
    try:
        # Validate the URL
        if not urlparse(url).scheme in ("http", "https"):
            logger.error(f"Invalid URL scheme for: {url}")
            return None

        response = requests.get(url)
        response.raise_for_status()

        original_filename = os.path.basename(urlparse(url).path) or "downloaded_torrent"
        tmp_file_path = os.path.join(tempfile.gettempdir(), f"{original_filename}_temp.torrent")

        with open(tmp_file_path, 'wb') as tmp_file:
            tmp_file.write(response.content)

        logger.info(f"Torrent file downloaded to temporary path: {tmp_file_path}")
        return tmp_file_path
    except requests.RequestException as e:
        logger.error(f"Error downloading torrent from {url}: {e}")
        return None


def determine_save_dir(info_hash, use_info_hash_folders):
    """
    Determines the directory for saving torrent files.

    Args:
        info_hash (str): The info hash of the torrent.
        use_info_hash_folders (bool): Whether to organize files into subdirectories.

    Returns:
        str: The relative directory path for saving torrent files.
    """
    if use_info_hash_folders:
        subdir_1, subdir_2 = info_hash[:2], info_hash[2:4]
        torrent_dir = os.path.join(settings.MEDIA_TORRENT, subdir_1, subdir_2)
    else:
        torrent_dir = settings.MEDIA_TORRENT

    full_path = os.path.join(settings.MEDIA_ROOT, torrent_dir)
    os.makedirs(full_path, exist_ok=True)

    logger.debug(f"Created or verified save directory: {full_path}")
    return torrent_dir



def create_torrent_instance(metadata, url, torrent_file, user):
    """
    Creates and saves a Torrent instance in the database.

    Args:
        metadata (dict): Torrent metadata returned from `process_torrent_file`.
        url (str): URL of the torrent file (if applicable).
        torrent_file (str): Relative path to the torrent file.
        user (User): User who uploaded the torrent.

    Returns:
        Torrent: The created Torrent instance.
    """
    try:
        logger.debug(f"Storing torrent file with relative path: {metadata['torrent_file_path']}")
        torrent = Torrent(
            info_hash=metadata["info_hash"],
            name=metadata["name"],
            slug=slugify(metadata["name"]),
            torrent_file=metadata["torrent_file_path"],  # Pass relative path directly
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
        logger.info(f"Torrent instance created successfully: {torrent.name}")
        return torrent
    except Exception as e:
        logger.error(f"Error creating torrent instance: {e}")
        return None


def _link_trackers_to_torrent(trackers, torrent_obj):
    """
    Link each tracker URL to the Torrent object and set announce_priority.

    Args:
        trackers (list): List of tracker tiers (each tier is a list of tracker URLs).
        torrent_obj (Torrent): The Torrent instance to link trackers to.
    """
    for level, tracker_list in enumerate(trackers):
        # Process each tracker URL in the tier
        for tracker_url in tracker_list:
            if tracker_url:
                try:
                    # Get or create the tracker in the database
                    tracker, _ = Tracker.objects.get_or_create(url=tracker_url)
                    torrent_obj.trackers.add(tracker)

                    # Add or update TrackerStat with announce priority
                    tracker_stat, _ = torrent_obj.trackerstat_set.get_or_create(
                        tracker=tracker,
                        defaults={'announce_priority': level}
                    )
                    # Ensure announce_priority is always updated
                    tracker_stat.announce_priority = level
                    tracker_stat.save()

                    logger.debug(f"Linked tracker {tracker_url} to torrent {torrent_obj.name} with priority {level}")
                except Exception as e:
                    logger.error(f"Error linking tracker {tracker_url} to torrent {torrent_obj.name}: {e}")


def process_torrent_file(torrent_file_path, save_dir):
    """Processes the torrent file, adds custom trackers, and saves it."""
    try:
        logger.info(f"Processing torrent file: {torrent_file_path}")
        t = Torrenttorf.read(torrent_file_path)
        logger.info(f"Parsed torrent file: {t.name}")

        # Add custom tracker if not already present
        custom_tracker = settings.TRACKER_ANNOUNCE
        if custom_tracker and custom_tracker not in [tracker for sublist in t.trackers for tracker in sublist]:
            t.trackers.append([custom_tracker])
            logger.info(f"Added custom tracker: {custom_tracker}")

        # Ensure the save directory exists
        absolute_save_dir = os.path.join(settings.MEDIA_ROOT, save_dir)
        os.makedirs(absolute_save_dir, exist_ok=True)

        # Save the torrent file
        absolute_save_path = os.path.join(absolute_save_dir, f"{t.name}.torrent")
        logger.debug(f"Saving torrent to absolute path: {absolute_save_path}")

        if os.path.exists(absolute_save_path):
            logger.warning(f"File already exists at: {absolute_save_path}. Removing old file.")
            os.remove(absolute_save_path)

        t.write(absolute_save_path)

        # Convert absolute path to relative path
        relative_path = os.path.relpath(absolute_save_path, settings.MEDIA_ROOT)
        logger.debug(f"Returning relative path for DB: {relative_path}")

        logger.info(f"Processed torrent file saved at: {absolute_save_path}")
        return {
            "info_hash": t.infohash,
            "name": t.name[:128],
            "torrent_file_path": relative_path,  # Return relative path
            "size": t.size,
            "pieces": t.pieces,
            "piece_size": t.piece_size,
            "magnet": str(t.magnet()),
            "file_list": [{"name": file.name, "size": file.size} for file in t.files],
            "file_count": len(t.files),
            "trackers": t.trackers,
        }
    except Exception as e:
        logger.error(f"Error processing torrent file: {e}")
        return None
