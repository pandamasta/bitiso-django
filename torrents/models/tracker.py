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
    last_seen = models.DateTimeField(
        null=True, blank=True,
        help_text="The last date when the tracker was successfully contacted (network-level reachability)."
    )
    last_try = models.DateTimeField(
        null=True, blank=True,
        help_text="The most recent attempt to contact the tracker (network-level or scrape)."
    )
    is_scrapable = models.BooleanField(
        default=True,
        help_text="Indicates whether the tracker supports scraping (managed manually or via analysis)."
    )

    class Meta:
        verbose_name = _("Tracker")
        verbose_name_plural = _("Trackers")
        ordering = ['url']

    def __str__(self):
        return self.url
