from django.core.management.base import BaseCommand
from ...models.torrent import Torrent
from ...models.tracker_stats import TrackerStat
from ...models.tracker import Tracker

from tracker_scraper import scrape
from bencodepy.exceptions import BencodeDecodeError
from urllib.parse import urlparse
import urllib3
import logging


logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # Define batch size for processing hashes


class Command(BaseCommand):
    help = "Scrape tracker and update stats"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tracker',
            type=str,
            help="Scrape a specific tracker by URL. If omitted, all trackers will be scraped."
        )
        parser.add_argument(
            '--hash',
            type=str,
            help="Scrape a specific torrent by info hash. If omitted, all torrents for the tracker will be scraped."
        )

    def handle(self, *args, **kwargs):
        tracker_url = kwargs.get('tracker')
        specific_hash = kwargs.get('hash')

        if tracker_url:
            try:
                tracker = Tracker.objects.get(url=tracker_url)
                self.process_tracker(tracker, specific_hash)
            except Tracker.DoesNotExist:
                logger.error(f"Tracker with URL {tracker_url} does not exist.")
        else:
            trackers = Tracker.objects.all()
            for tracker in trackers:
                self.process_tracker(tracker, specific_hash)

    def process_tracker(self, tracker, specific_hash=None):
        """Process scraping for a single tracker."""
        hashes = self.get_hashes_for_tracker(tracker, specific_hash)
        if not hashes:
            logger.info(f"No torrents for tracker: {tracker.url}")
            return

        scrape_results = {}
        for i in range(0, len(hashes), BATCH_SIZE):
            batch = hashes[i:i + BATCH_SIZE]
            try:
                batch_results = scrape(tracker=tracker.url, hashes=batch)
                scrape_results.update(batch_results)
            except TimeoutError:
                logger.error(f"Timeout Error with tracker: {tracker.url}")
            except BencodeDecodeError:
                logger.error(f"Invalid bencoded data from tracker: {tracker.url}")
            except (ConnectionRefusedError, urllib3.exceptions.NewConnectionError) as e:
                logger.error(f"Connection Error with tracker: {tracker.url} - {e}")
            except Exception as e:
                logger.error(f"Unexpected error with tracker: {tracker.url} - {e}")

        self.update_tracker_stats(tracker.id, scrape_results)

    def get_hashes_for_tracker(self, tracker, specific_hash=None):
        """Fetch hashes for the given tracker, optionally filtered by a specific hash."""
        if specific_hash:
            # Validate the specific hash
            if not TrackerStat.objects.filter(tracker=tracker, torrent__info_hash=specific_hash).exists():
                logger.warning(f"Hash {specific_hash} not found for tracker {tracker.url}.")
                return []

            return [specific_hash]

        # Fetch all hashes for the tracker
        return list(
            TrackerStat.objects.filter(tracker=tracker).values_list("torrent__info_hash", flat=True)
        )

    def update_tracker_stats(self, tracker_id, scrape_results):
        """Update TrackerStat and Torrent models with scrape results."""
        tracker_stats_to_update = []
        torrents_to_update = []

        for info_hash, stats in scrape_results.items():
            try:
                torrent_obj = Torrent.objects.get(info_hash=info_hash)
                tracker_stat = TrackerStat.objects.get(tracker_id=tracker_id, torrent_id=torrent_obj.id)

                tracker_stat.seed = stats.get("seeds", 0)
                tracker_stat.leech = stats.get("peers", 0)
                tracker_stat.complete = stats.get("complete", 0)
                tracker_stats_to_update.append(tracker_stat)

                # Update Torrent's stats as well
                torrent_obj.seed_count = stats.get("seeds", 0)
                torrent_obj.leech_count = stats.get("peers", 0)
                torrents_to_update.append(torrent_obj)
            except Torrent.DoesNotExist:
                logger.warning(f"Torrent with hash {info_hash} not found.")
            except TrackerStat.DoesNotExist:
                logger.warning(f"TrackerStat not found for hash {info_hash} on tracker {tracker_id}.")

        # Bulk update tracker stats
        if tracker_stats_to_update:
            TrackerStat.objects.bulk_update(tracker_stats_to_update, ["seed", "leech", "complete"])

        # Bulk update torrent stats
        if torrents_to_update:
            Torrent.objects.bulk_update(torrents_to_update, ["seed_count", "leech_count"])


