#torrents/models/tracker.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class Tracker(models.Model):
    """
    Tracker info.
    """
    url = models.URLField(_("URL"), max_length=1000)

    is_reachable = models.BooleanField(
        default=True,
        help_text="Indicates whether the tracker is reachable at the network level."
    )
    is_scrapable = models.BooleanField(
        default=True,
        help_text="Indicates whether the tracker supports scraping."
    )
    last_try_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Last attempt to scrape the tracker."
    )
    last_successful_scrape = models.DateTimeField(
        null=True, blank=True,
        help_text="The most recent date when scraping succeeded."
    )
    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed scrape attempts."
    )

    class Meta:
        verbose_name = _("Tracker")
        verbose_name_plural = _("Trackers")
        ordering = ['url']

    def __str__(self):
        return self.url
