#torrents/models/tracker_stats.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from .torrent import Torrent
from .tracker import Tracker

class TrackerStat(models.Model):
    """
    Torrent statistics on trackers.
    """
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE)
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    announce_priority = models.IntegerField(_("Announce priority"), default=0) #level
    seed = models.PositiveIntegerField(_("Number of seeds"), default=0)
    leech = models.PositiveIntegerField(_("Number of leeches"), default=0)
    complete = models.PositiveIntegerField(_("Complete"), default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['torrent', 'tracker'], name='unique_torrent_tracker')
        ]
        verbose_name = _("Tracker Stat")
        verbose_name_plural = _("Tracker Stats")
        ordering = ['torrent', 'tracker']

    def __str__(self):
        return f"TrackerStat for {self.tracker.url} in {self.torrent.name}"

