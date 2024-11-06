import os
import logging
from torf import Torrent as Torrenttorf, BdecodeError, ReadError, WriteError
from django.conf import settings
from django.core.exceptions import ValidationError
from torrents.models import Torrent, Tracker
from torrents.models import Tracker, TrackerStat
import uuid

# Set up logging
logger = logging.getLogger(__name__)


def process_torrent_file(torrent_file_path, user, save_dir=None):
    try:
        logger.info(f"Processing torrent file: {torrent_file_path}")

        # Load and parse the torrent
        t = Torrenttorf.read(torrent_file_path)
        logger.info(f"Parsed torrent file: {t.name}")

        # Ensure custom tracker is added to the list
        custom_tracker = settings.TRACKER_ANNOUNCE
        trackers_set = {tracker for sublist in t.trackers for tracker in sublist}
        if custom_tracker not in trackers_set:
            t.trackers.append([custom_tracker])
            logger.info(f"Added custom tracker: {custom_tracker}")

        # Define the save path using the save directory and name
        if save_dir:
            save_path = os.path.join(settings.MEDIA_ROOT, save_dir, f"{t.name}.torrent")
        else:
            save_path = os.path.join(settings.MEDIA_TORRENT, f"{t.name}.torrent")

        # Save the modified torrent file with custom trackers
        if os.path.exists(save_path):
            logger.info(f"File already exists at: {save_path}. Skipping save.")
            return None

        t.write(save_path)
        logger.info(f"Processed torrent file saved at: {save_path}")

        # Return metadata with trackers for further processing
        return {
            "info_hash": t.infohash,
            "name": t.name[:128],
            "size": t.size,
            "pieces": t.pieces,
            "piece_size": t.piece_size,
            "magnet": str(t.magnet()),
            "torrent_filename": os.path.relpath(save_path, settings.MEDIA_ROOT),
            "file_list": [{"name": file.name, "size": file.size} for file in t.files],
            "file_count": len(t.files),
            "trackers": t.trackers
        }
    except Exception as e:
        logger.error(f"Error processing torrent file: {e}")
        return None


# def _link_trackers_to_torrent(trackers, torrent_obj):
#     """
#     Link each tracker URL to the Torrent object with the specified level.
#     """
#     for level, sublist in enumerate(trackers):
#         for tracker_url in sublist:
#             if tracker_url:
#                 tracker, created = Tracker.objects.get_or_create(url=tracker_url)
#                 torrent_obj.trackers.add(tracker)
#                 # Create or update TrackerStat with the level field
#                 tracker_stat, _ = torrent_obj.trackerstat_set.get_or_create(
#                     tracker=tracker, defaults={'level': level}
#                 )
#                 tracker_stat.level = level
#                 tracker_stat.save()
#                 logger.debug(f"Linked tracker {tracker_url} to torrent {torrent_obj.name} at level {level}")
