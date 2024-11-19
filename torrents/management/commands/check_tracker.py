from django.core.management.base import BaseCommand
from ...models.tracker import Tracker
from urllib.parse import urlparse
import socket
import logging
from django.utils.timezone import now

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Only log messages at INFO level or higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)

SOCKET_TIMEOUT = 5


class Command(BaseCommand):
    help = "Check connectivity for all trackers and update their reachability status."

    def handle(self, *args, **options):
        # Prefetch trackers to avoid redundant queries
        trackers = list(Tracker.objects.all())
        logger.info(f"Checking connectivity for {len(trackers)} trackers.")

        for tracker in trackers:
            self.check_connectivity(tracker)

    def check_connectivity(self, tracker):
        """Check tracker connectivity."""
        parsed_url = urlparse(tracker.url)
        host = parsed_url.hostname
        scheme = parsed_url.scheme
        port = parsed_url.port or (443 if scheme == 'https' else 80)

        if scheme == 'udp':
            # Skip UDP connectivity checks, mark as reachable
            Tracker.objects.filter(id=tracker.id).update(is_reachable=True)
            logger.info(f"Skipping connectivity check for UDP tracker: {tracker.url}. Marked as reachable by default.")
            return

        try:
            # Attempt to connect to the tracker
            conn = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
            conn.close()

            # Update tracker as reachable
            Tracker.objects.filter(id=tracker.id).update(
                is_reachable=True,
                last_seen=now(),
                last_try=now()
            )
            logger.info(f"Tracker {tracker.id} ({tracker.url}) is reachable.")

        except (socket.timeout, OSError) as e:
            # Update tracker as not reachable
            Tracker.objects.filter(id=tracker.id).update(
                is_reachable=False,
                last_try=now()
            )
            logger.warning(f"Tracker {tracker.id} ({tracker.url}) is not reachable: {e}")

