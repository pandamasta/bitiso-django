#torrents/models/tracker.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class Tracker(models.Model):
    """
    Tracker info.
    """
    AUTOMATIC = 'automatic'
    MANUAL = 'manual'

    MODE_CHOICES = [
        (AUTOMATIC, 'Automatic'),
        (MANUAL, 'Manual'),
    ]

    url = models.URLField(_("URL"), max_length=1000)

    is_reachable = models.BooleanField(
        default=True,
        help_text="Indicates whether the tracker is reachable at the network level."
    )
    is_reachable_mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default=AUTOMATIC,
        help_text="Indicates whether the is_reachable field is managed automatically or manually."
    )

    is_scrapable = models.BooleanField(
        default=True,
        help_text="Indicates whether the tracker supports scraping (managed manually or via analysis)."
    )
    is_scrapable_mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default=AUTOMATIC,
        help_text="Indicates whether the is_scrapable field is managed automatically or manually."
    )

    last_seen = models.DateTimeField(
        null=True, blank=True,
        help_text="The last date when the tracker was successfully contacted (network-level reachability)."
    )
    last_try = models.DateTimeField(
        null=True, blank=True,
        help_text="The most recent attempt to contact the tracker (network-level or scrape)."
    )

    class Meta:
        verbose_name = _("Tracker")
        verbose_name_plural = _("Trackers")
        ordering = ['url']

    def __str__(self):
        return self.url

