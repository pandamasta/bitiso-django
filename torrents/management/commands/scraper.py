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
    help = "Scrape tracker, update stats, and recheck connectivity/scrapable status."

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
        parser.add_argument(
            '--only-availability',
            action='store_true',
            help="Only update tracker availability without performing scraping."
        )
        parser.add_argument(
            '--bypass-scrapable-check',
            action='store_true',
            help="Bypass the scrapable and retry interval check to force scraping of all trackers."
        )
        parser.add_argument(
            '--recheck',
            type=str,
            choices=['connectivity', 'scrapable'],
            help="Recheck connectivity or scrapable status for trackers."
        )

    def handle(self, *args, **options):
        tracker_url = options.get('tracker')
        specific_hash = options.get('hash')
        only_availability = options.get('only-availability')
        bypass_scrapable_check = options.get('bypass-scrapable-check')
        recheck = options.get('recheck')

        trackers_processed = 0
        trackers_skipped = 0
        torrents_updated = 0

        trackers = [Tracker.objects.get(url=tracker_url)] if tracker_url else Tracker.objects.all()

        for tracker in trackers:
            if recheck:
                self.recheck_tracker(tracker, recheck)
                continue

            if only_availability:
                self.update_tracker_availability(tracker)
                continue

            logger.info(f"Processing tracker: {tracker.url}")
            result = self.process_tracker(tracker, specific_hash, bypass_scrapable_check)
            if result == -1:
                trackers_skipped += 1
            else:
                trackers_processed += 1
                torrents_updated += result

        logger.info("Tracker processing completed.")
        logger.info(f"Summary:")
        logger.info(f"- Trackers processed: {trackers_processed}")
        logger.info(f"- Trackers skipped: {trackers_skipped}")
        logger.info(f"- Torrents updated: {torrents_updated}")

    def recheck_tracker(self, tracker, recheck_type):
        """Recheck either connectivity or scrapable status for a tracker."""
        logger.info(f"Rechecking tracker: {tracker.url} for {recheck_type} status.")

        if recheck_type == 'connectivity':
            self.update_tracker_availability(tracker)
        elif recheck_type == 'scrapable':
            # Attempt a test scrape with a dummy hash to check if the tracker supports scraping
            dummy_hash = "0000000000000000000000000000000000000000"
            logger.debug(f"Testing scrapable status with dummy hash for tracker: {tracker.url}")
            hashes = [dummy_hash]

            scrape_url = tracker.url.replace('/announce', '/scrape')
            try:
                scrape_results = scrape(tracker=scrape_url, hashes=hashes)
                if scrape_results:
                    tracker.is_scrapable = True
                    tracker.last_successful_scrape = now()
                    tracker.failed_attempts = 0
                    logger.info(f"Tracker {tracker.url} is confirmed scrapable.")
                else:
                    tracker.is_scrapable = False
                    logger.warning(f"Tracker {tracker.url} returned no scrape results. Marked as not scrapable.")
            except Exception as e:
                tracker.is_scrapable = False
                logger.error(f"Error while testing scrapable status for tracker {tracker.url}: {e}")

            tracker.last_try_date = now()
            tracker.save()

    def process_tracker(self, tracker, specific_hash=None, bypass_scrapable_check=False):
        """Process scraping for a single tracker."""
        if not bypass_scrapable_check:
            if not tracker.is_reachable:
                logger.info(f"Skipping tracker {tracker.url} as it is not reachable.")
                return -1
            if not tracker.is_scrapable and tracker.last_try_date and tracker.last_try_date > now() - MAX_RETRIES_INTERVAL:
                logger.info(f"Skipping tracker {tracker.url} as it's marked not scrapable and retry interval hasn't passed.")
                return -1

        tracker.last_try_date = now()
        tracker.save()

        hashes = self.get_hashes_for_tracker(tracker, specific_hash)
        if not hashes:
            logger.info(f"No torrents found for tracker: {tracker.url}")
            return 0

        logger.debug(f"Starting scrape for tracker: {tracker.url} with {len(hashes)} hashes.")

        scrape_results = {}
        scrape_url = tracker.url.replace('/announce', '/scrape')
        for i in range(0, len(hashes), BATCH_SIZE):
            batch = hashes[i:i + BATCH_SIZE]
            logger.debug(f"Scraping batch of {len(batch)} hashes for tracker: {scrape_url}")
            try:
                batch_results = scrape(tracker=scrape_url, hashes=batch)
                logger.debug(f"Raw scrape results from {scrape_url}: {batch_results}")
                scrape_results.update(batch_results)
            except Exception as e:
                logger.error(f"Error scraping tracker {scrape_url}: {e}")
                tracker.failed_attempts += 1
                tracker.save()
                return 0

        if scrape_results:
            updated_count = self.update_tracker_stats(tracker.id, scrape_results)
            tracker.is_scrapable = True
            tracker.last_successful_scrape = now()
            tracker.failed_attempts = 0
            tracker.save()
            return updated_count
        else:
            logger.warning(f"No scrape results received for tracker: {scrape_url}.")
            tracker.is_scrapable = False
            tracker.save()
            return 0


    def is_tracker_reachable(self, tracker):
        """Test if a tracker is reachable based on its URL scheme."""
        parsed_url = urlparse(tracker.url)
        host = parsed_url.hostname
        scheme = parsed_url.scheme
        port = parsed_url.port or (443 if scheme == 'https' else 80)

        if scheme in ('http', 'https'):
            try:
                conn = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
                conn.close()
                logger.debug(f"Tracker {tracker.url} is reachable on port {port}.")
                tracker.is_reachable = True
                tracker.failed_attempts = 0  # Reset on success
                tracker.save()
                return True
            except (socket.timeout, OSError) as e:
                logger.debug(f"Tracker {tracker.url} is not reachable: {e}")
                tracker.is_reachable = False
                tracker.failed_attempts += 1
                tracker.save()
                return False
        elif scheme == 'udp':
            logger.warning(f"Cannot verify reachability of UDP tracker: {tracker.url}")
            return True  # Assume reachable for UDP as no easy way to verify
        else:
            logger.warning(f"Unsupported tracker scheme: {scheme} for tracker {tracker.url}")
            tracker.is_reachable = False
            tracker.save()
            return False

    def update_tracker_availability(self, tracker):
        """Update the availability of a tracker without scraping."""
        is_reachable = self.is_tracker_reachable(tracker)
        tracker.is_reachable = is_reachable
        tracker.last_try_date = now()
        tracker.save()
        if is_reachable:
            logger.info(f"Tracker {tracker.url} is reachable.")
        else:
            logger.warning(f"Tracker {tracker.url} is not reachable.")

    def get_hashes_for_tracker(self, tracker, specific_hash=None):
        """Fetch hashes for the given tracker, optionally filtered by a specific hash."""
        if specific_hash:
            logger.debug(f"Filtering hashes for specific hash: {specific_hash}")
            if not TrackerStat.objects.filter(tracker=tracker, torrent__info_hash=specific_hash).exists():
                logger.warning(f"Hash {specific_hash} not found for tracker {tracker.url}.")
                return []
            return [specific_hash]

        hashes = list(TrackerStat.objects.filter(tracker=tracker).values_list("torrent__info_hash", flat=True))
        logger.debug(f"Retrieved {len(hashes)} hashes for tracker: {tracker.url}")
        return hashes

    def update_tracker_stats(self, tracker_id, scrape_results):
        """Update TrackerStat and Torrent models with scrape results."""
        tracker_stats_to_update = []
        torrents_to_update = []

        tracker = Tracker.objects.get(id=tracker_id)
        for info_hash, stats in scrape_results.items():
            try:
                torrent = Torrent.objects.get(info_hash=info_hash)
                tracker_stat = TrackerStat.objects.get(tracker=tracker, torrent=torrent)

                tracker_stat.seed = stats.get("seeds", 0)
                tracker_stat.leech = stats.get("peers", 0)
                tracker_stat.complete = stats.get("complete", 0)
                tracker_stats_to_update.append(tracker_stat)

                torrent.seed_count = stats.get("seeds", 0)
                torrent.leech_count = stats.get("peers", 0)
                torrents_to_update.append(torrent)
            except Exception as e:
                logger.error(f"Error updating stats for hash {info_hash} on tracker {tracker.url}: {e}")

        TrackerStat.objects.bulk_update(tracker_stats_to_update, ["seed", "leech", "complete"])
        Torrent.objects.bulk_update(torrents_to_update, ["seed_count", "leech_count"])
        return len(torrents_to_update)
