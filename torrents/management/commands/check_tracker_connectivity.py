from django.core.management.base import BaseCommand
from ...models.tracker import Tracker
from urllib.parse import urlparse
import socket
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

SOCKET_TIMEOUT = 5


class Command(BaseCommand):
    help = "Check connectivity for all trackers and update their reachability status."

    def handle(self, *args, **options):
        trackers = Tracker.objects.all()
        for tracker in trackers:
            self.check_connectivity(tracker)

    def check_connectivity(self, tracker):
        """Check tracker connectivity."""
        parsed_url = urlparse(tracker.url)
        host = parsed_url.hostname
        scheme = parsed_url.scheme
        port = parsed_url.port or (443 if scheme == 'https' else 80)

        if scheme == 'udp':
            # Assume UDP trackers are reachable unless proven otherwise
            tracker.is_reachable = True
            logger.warning(f"Skipping connectivity check for UDP tracker: {tracker.url}. Marked as reachable by default.")
        else:
            try:
                conn = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
                conn.close()
                tracker.is_reachable = True
                tracker.last_seen = now()
                tracker.last_try = now()
                logger.info(f"Tracker {tracker.url} is reachable.")
            except (socket.timeout, OSError) as e:
                tracker.is_reachable = False
                tracker.last_try = now()
                logger.warning(f"Tracker {tracker.url} is not reachable: {e}")

        tracker.save()
