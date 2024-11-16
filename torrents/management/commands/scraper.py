from django.core.management.base import BaseCommand
from ...models.torrent import Torrent
from ...models.tracker_stats import TrackerStat
from ...models.tracker import Tracker
from tracker_scraper import scrape
from bencodepy.exceptions import BencodeDecodeError
from urllib.parse import urlparse
import urllib3
import socket
import logging
from datetime import timedelta
from django.utils.timezone import now

logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # Define batch size for processing hashes
SOCKET_TIMEOUT = 5  # Timeout for socket test in seconds
MAX_RETRIES_INTERVAL = timedelta(days=7)  # Retry every 7 days for unresponsive trackers


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

    def handle(self, *args, **options):
        tracker_url = options.get('tracker')
        specific_hash = options.get('hash')

        if tracker_url:
            try:
                tracker = Tracker.objects.get(url=tracker_url)
                logger.info(f"Processing single tracker: {tracker.url}")
                self.process_tracker(tracker, specific_hash)
            except Tracker.DoesNotExist:
                logger.error(f"Tracker with URL {tracker_url} does not exist.")
        else:
            logger.info("Processing all trackers...")
            trackers = Tracker.objects.all()
            for tracker in trackers:
                self.process_tracker(tracker, specific_hash)

    def process_tracker(self, tracker, specific_hash=None):
        """Process scraping for a single tracker."""
        # Skip trackers marked as not scrapable and within retry interval
        if not tracker.is_scrapable and tracker.last_try_date and tracker.last_try_date > now() - MAX_RETRIES_INTERVAL:
            logger.info(f"Skipping tracker {tracker.url} as it's marked not scrapable and retry interval hasn't passed.")
            return

        # Update the last_try_date
        tracker.last_try_date = now()
        tracker.save()

        # Test if the tracker is reachable
        if not self.is_tracker_reachable(tracker):
            logger.warning(f"Tracker {tracker.url} is not reachable. Marking as not scrapable.")
            tracker.is_scrapable = False
            tracker.save()
            return

        hashes = self.get_hashes_for_tracker(tracker, specific_hash)
        if not hashes:
            logger.info(f"No torrents found for tracker: {tracker.url}")
            return

        logger.debug(f"Starting scrape for tracker: {tracker.url} with {len(hashes)} hashes.")

        scrape_results = {}
        for i in range(0, len(hashes), BATCH_SIZE):
            batch = hashes[i:i + BATCH_SIZE]
            logger.debug(f"Scraping batch of {len(batch)} hashes for tracker: {tracker.url}")
            try:
                batch_results = scrape(tracker=tracker.url, hashes=batch)
                scrape_results.update(batch_results)
                logger.debug(f"Scrape successful for tracker: {tracker.url}")
            except TimeoutError:
                logger.warning(f"Timeout while scraping tracker: {tracker.url}")
                tracker.is_scrapable = False
                tracker.save()
                return
            except BencodeDecodeError:
                logger.warning(f"Invalid bencoded data received from tracker: {tracker.url}")
                tracker.is_scrapable = False
                tracker.save()
                return
            except (ConnectionRefusedError, urllib3.exceptions.NewConnectionError) as e:
                logger.warning(f"Network error with tracker {tracker.url}: {e}")
                tracker.is_scrapable = False
                tracker.save()
                return
            except Exception as e:
                logger.error(f"Unexpected error while scraping tracker {tracker.url}: {e}")
                tracker.is_scrapable = False
                tracker.save()
                return

        if scrape_results:
            logger.info(f"Scrape completed for tracker: {tracker.url}. Updating stats...")
            self.update_tracker_stats(tracker.id, scrape_results)
            tracker.is_scrapable = True
        else:
            logger.warning(f"No scrape results received for tracker: {tracker.url}. Marking as not scrapable.")
            tracker.is_scrapable = False

        tracker.save()

    def is_tracker_reachable(self, tracker):
        """Test if a tracker is reachable using a socket connection."""
        parsed_url = urlparse(tracker.url)
        host = parsed_url.hostname
        port = parsed_url.port or 80  # Default to 80 if no port is provided

        try:
            with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT):
                logger.debug(f"Tracker {tracker.url} is reachable.")
                return True
        except (socket.timeout, OSError) as e:
            logger.debug(f"Tracker {tracker.url} is not reachable: {e}")
            return False

    def get_hashes_for_tracker(self, tracker, specific_hash=None):
        """Fetch hashes for the given tracker, optionally filtered by a specific hash."""
        if specific_hash:
            logger.debug(f"Filtering hashes for specific hash: {specific_hash}")
            if not TrackerStat.objects.filter(tracker=tracker, torrent__info_hash=specific_hash).exists():
                logger.warning(f"Hash {specific_hash} not found for tracker {tracker.url}.")
                return []

            return [specific_hash]

        hashes = list(
            TrackerStat.objects.filter(tracker=tracker).values_list("torrent__info_hash", flat=True)
        )
        logger.debug(f"Retrieved {len(hashes)} hashes for tracker: {tracker.url}")
        return hashes

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

                torrent_obj.seed_count = stats.get("seeds", 0)
                torrent_obj.leech_count = stats.get("peers", 0)
                torrents_to_update.append(torrent_obj)

                logger.debug(f"Updated stats for hash: {info_hash}")
            except Torrent.DoesNotExist:
                logger.warning(f"Torrent with hash {info_hash} not found.")
            except TrackerStat.DoesNotExist:
                logger.warning(f"TrackerStat not found for hash {info_hash} on tracker {tracker_id}.")

        if tracker_stats_to_update:
            TrackerStat.objects.bulk_update(tracker_stats_to_update, ["seed", "leech", "complete"])
            logger.info(f"Updated {len(tracker_stats_to_update)} TrackerStat records for tracker {tracker_id}")

        if torrents_to_update:
            Torrent.objects.bulk_update(torrents_to_update, ["seed_count", "leech_count"])
            logger.info(f"Updated {len(torrents_to_update)} Torrent records.")
