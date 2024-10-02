# models/external_torrent.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class ExternalTorrent(models.Model):
    url = models.CharField(_("URL of external torrent"), max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.url
