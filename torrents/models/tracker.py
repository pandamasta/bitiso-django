#torrents/models/tracker.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class Tracker(models.Model):
    """
    Tracker info.
    """
    url = models.URLField(_("URL"), max_length=1000)
    
    is_scrapable = models.BooleanField(default=True, help_text="Indicates whether the tracker is currently scrapable.")
    last_try_date = models.DateTimeField(null=True, blank=True, help_text="Last attempt to scrape the tracker.")

    class Meta:
        verbose_name = _("Tracker")
        verbose_name_plural = _("Trackers")
        ordering = ['url']

    def __str__(self):
        return self.url

