# models/tracker.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class Tracker(models.Model):
    """
    Tracker info.
    """
    url = models.CharField(_("URL"), max_length=1000)

    def __str__(self):
        return self.url
