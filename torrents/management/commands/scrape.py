from django.core.management.base import BaseCommand
from ...models.torrent import Torrent
from ...models.tracker_stats import TrackerStat
from ...models.tracker import Tracker
from tracker_scraper import scrape
from bencodepy.exceptions import BencodeDecodeError
import urllib3
from django.utils.timezone import now
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Only log messages at INFO level or higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape trackers and update stats"

    def handle(self, *args, **kwargs):
        # Prepare a dictionary for scraping results
        scrape_dict = {}

        # Process only reachable trackers
        for tracker in Tracker.objects.filter(is_reachable=True):
            scrape_dict[tracker.id] = {}
            hashes = []

            # Collect info hashes for the tracker
            for torrent in TrackerStat.objects.filter(tracker_id=tracker.id):
                hashes.append(torrent.torrent.info_hash)

            if not hashes:
                logger.info(f"No torrents found for tracker: {tracker.url}")
                continue

            try:
                # Perform the scrape and store results
                logger.info(f"Scraping tracker: {tracker.url}")
                scrape_dict[tracker.id] = scrape(tracker=tracker.url, hashes=hashes)
            except TimeoutError:
                logger.warning(f"Timeout Error with tracker: {tracker.url}")
            except BencodeDecodeError:
                logger.error(f"Invalid bencoded data received from tracker: {tracker.url}")
            except ConnectionRefusedError:
                logger.error(f"Connection Refused Error: Could not connect to tracker: {tracker.url}")
            except urllib3.exceptions.NewConnectionError as e:
                logger.error(f"Network Error: Failed to establish a new connection to {tracker.url}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected Error: {str(e)}")
            finally:
                hashes = []  # Clear the hashes list for the next iteration

        # Update database with scrape results
        for tracker_id, scrape_results in scrape_dict.items():
            for info_hash, stats in scrape_results.items():
                try:
                    torrent_obj = Torrent.objects.get(info_hash=info_hash)
                    tracker_stat = TrackerStat.objects.get(tracker_id=tracker_id, torrent_id=torrent_obj.id)

                    # Update scrape statistics
                    tracker_stat.seed = stats.get("seeds", 0)
                    tracker_stat.leech = stats.get("peers", 0)
                    tracker_stat.complete = stats.get("complete", 0)
                    tracker_stat.last_scrape_attempt = now()
                    tracker_stat.last_successful_scrape = now()
                    tracker_stat.save()

                    logger.info(f"Updated stats for torrent {info_hash} on tracker {tracker_stat.tracker.url}")
                except TrackerStat.DoesNotExist:
                    logger.warning(f"TrackerStat does not exist for torrent {info_hash} on tracker {tracker_id}")
                except Torrent.DoesNotExist:
                    logger.error(f"Torrent with info hash {info_hash} not found.")
                except Exception as e:
                    logger.error(f"Error updating stats for hash {info_hash}: {e}")

