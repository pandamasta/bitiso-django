from django.core.management.base import BaseCommand
from ...models.torrent import Torrent
from django.db.models import Max
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Only log messages at INFO level or higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update Torrent seed and leech values based on the highest counts from TrackerStats"

    def handle(self, *args, **kwargs):
        logger.info("Starting seed and leech aggregation for torrents.")

        torrents_to_update = []

        # Annotate torrents with their maximum seed and leech values
        torrents_with_stats = Torrent.objects.annotate(
            max_seed=Max('trackerstat__seed'),
            max_leech=Max('trackerstat__leech')
        )

        for torrent in torrents_with_stats:
            # Get the annotated maximum seed and leech values
            max_seed = torrent.max_seed or 0
            max_leech = torrent.max_leech or 0

            logger.debug(f"Torrent ID {torrent.id}: Current seed={torrent.seed_count}, leech={torrent.leech_count}. "
                         f"Annotated max seed={max_seed}, max leech={max_leech}.")

            # Only update if the values have changed
            if torrent.seed_count != max_seed or torrent.leech_count != max_leech:
                logger.info(f"Updating Torrent ID {torrent.id}: "
                            f"seed {torrent.seed_count} -> {max_seed}, leech {torrent.leech_count} -> {max_leech}.")
                torrent.seed_count = max_seed
                torrent.leech_count = max_leech
                torrents_to_update.append(torrent)

        # Bulk update torrents with updated stats
        if torrents_to_update:
            Torrent.objects.bulk_update(torrents_to_update, ['seed_count', 'leech_count'])
            logger.info(f"Updated {len(torrents_to_update)} Torrent records with highest seed and leech values.")
        else:
            logger.info("No Torrent records needed updating.")

        logger.info("Seed and leech aggregation for torrents completed.")
