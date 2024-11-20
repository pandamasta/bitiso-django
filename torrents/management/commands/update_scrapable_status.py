from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from ...models.tracker_stats import TrackerStat
from ...models.tracker import Tracker
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

SUCCESS_THRESHOLD = 10  # Percentage threshold for determining scrapability


class Command(BaseCommand):
    help = "Recalculate and suggest updates for tracker scrapable status based on success rates."

    def handle(self, *args, **options):
        trackers = Tracker.objects.all()
        updates = []

        # Collect trackers to update
        to_update = []

        for tracker in trackers:
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
                logger.warning(
                    f"Tracker {tracker.url} has no scrape attempts recorded. Marking as not scrapable."
                )
                tracker.is_scrapable = False
                to_update.append(tracker)

        # Perform bulk update for efficiency
        if to_update:
            Tracker.objects.bulk_update(to_update, ['is_scrapable'])
            logger.info("Bulk update completed for scrapable status.")

        # Log suggested updates
        if updates:
            logger.info("Suggested updates for scrapable status:")
            for url, old_status, new_status in updates:
                logger.info(f" - {url}: {old_status} -> {new_status}")
        else:
            logger.info("No changes required for tracker scrapable status.")
