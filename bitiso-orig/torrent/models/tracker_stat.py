# models/tracker_stat.py

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
    level = models.IntegerField(_("Announce level"), default=0)
    seed = models.IntegerField(_("Number of seeds"), default=0)
    leech = models.IntegerField(_("Number of leeches"), default=0)
    complete = models.IntegerField(_("Complete"), default=0)

    class Meta:
        unique_together = ('torrent', 'tracker')

    def __str__(self):
        return f"TrackerStat for {self.tracker.url} in {self.torrent.name}"
