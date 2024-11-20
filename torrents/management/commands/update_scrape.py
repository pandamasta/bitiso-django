from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from ...models.tracker_stats import TrackerStat
from ...models.tracker import Tracker
from django.utils.timezone import now
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Only log messages at INFO level or higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)

SUCCESS_THRESHOLD = 10  # Percentage threshold for determining scrapability


class Command(BaseCommand):
    help = "Recalculate and suggest updates for tracker scrapable status based on success rates."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Preview changes without applying them."
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        trackers = Tracker.objects.all()
        updates = []

        # Collect trackers to update
        to_update = []

        for tracker in trackers:
            try:
                # Aggregate total attempts and successful scrapes
                stats = TrackerStat.objects.filter(tracker=tracker).aggregate(
                    total_attempts=Count('id'),
                    successful_scrapes=Count('id', filter=Q(last_successful_scrape__isnull=False))
                )
                total_attempts = stats['total_attempts']
                successful_scrapes = stats['successful_scrapes']

                if total_attempts > 0:
                    # Calculate success rate
                    success_rate = (successful_scrapes / total_attempts) * 100
                    current_status = tracker.is_scrapable
                    new_status = success_rate >= SUCCESS_THRESHOLD

                    if current_status != new_status:
                        updates.append((tracker.url, current_status, new_status))
                        tracker.is_scrapable = new_status
                        to_update.append(tracker)

                    logger.info(
                        f"Tracker {tracker.url}: Success rate = {success_rate:.2f}%. "
                        f"Scrapable status: {'Updated' if current_status != new_status else 'Unchanged'}."
                    )
                else:
                    # Handle trackers with no recorded scrape attempts
                    logger.info(
                        f"Tracker {tracker.url} has no scrape attempts recorded. Marking as not scrapable."
                    )
                    tracker.is_scrapable = False
                    to_update.append(tracker)
            except Exception as e:
                logger.error(f"Error processing tracker {tracker.url}: {e}")

        # Perform bulk update for efficiency
        if to_update:
            if dry_run:
                logger.info(f"Dry Run: {len(to_update)} Tracker records would be updated.")
            else:
                Tracker.objects.bulk_update(to_update, ['is_scrapable'])
                logger.info(f"Bulk update completed for {len(to_update)} trackers.")

        # Log suggested updates
        if updates:
            logger.info("Suggested updates for scrapable status:")
            for url, old_status, new_status in updates:
                logger.info(f" - {url}: {old_status} -> {new_status}")
        else:
            logger.info("No changes required for tracker scrapable status.")

