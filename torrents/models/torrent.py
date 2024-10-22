#torrents/models/torrent.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..models.category import Category
from ..models.project import Project
from ..utils.slug_utils import generate_unique_slug

class Torrent(models.Model):
    """
    Torrent data model.
    """
    info_hash = models.CharField(_("SHA1 of torrent"), max_length=40, unique=True)
    name = models.CharField(_("Name"), max_length=128)
    slug = models.SlugField(blank=True, null=True, unique=True)
    size = models.PositiveBigIntegerField(_("Size in bytes"), default=0)
    pieces = models.PositiveIntegerField(_("Number of pieces"), default=1)
    piece_size = models.PositiveIntegerField(_("Piece size in bytes"), default=0)
    magnet = models.TextField(_("Magnet URI"), default="N/A")
    torrent_filename = models.CharField(_("Torrent file name"), max_length=128, default="N/A")
    comment = models.CharField(_("Comment"), max_length=256, default="N/A")
    trackers = models.ManyToManyField('Tracker', through="TrackerStat")
    file_list = models.TextField(_("List of files"), default="N/A")
    file_count = models.PositiveIntegerField(_("Number of files"), default=1)

    # Descriptive fields
    category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_("Show in the front end"), default=False)
    is_bitiso = models.BooleanField(_("Created by bitiso?"), default=True)
    description = models.TextField(_("Description"), blank=True, default='')
    website_url = models.URLField(_("Official website URL"), max_length=2000, blank=True, null=True)
    website_url_download = models.URLField(_("Download page URL"), max_length=2000, blank=True)
    website_url_repo = models.URLField(_("Repository URL"), max_length=2000, blank=True)
    version = models.CharField(_("Version of the software"), max_length=16, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(_("Deletion timestamp"), blank=True, null=True)
    
    # Uploader relation
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Uploader"),
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    # Statistics
    seed_count = models.PositiveIntegerField(_("Number of seeds"), default=0)
    leech_count = models.PositiveIntegerField(_("Number of leeches"), default=0)
    download_count = models.PositiveIntegerField(_("Number of downloads"), default=0)
    completion_count = models.PositiveIntegerField(_("Number of completions"), default=0)

    # Project relation
    project = models.ForeignKey(Project, verbose_name=_("Project"), null=True, on_delete=models.PROTECT, related_name='torrents')

    class Meta:
        verbose_name = _("Torrent")
        verbose_name_plural = _("Torrents")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Hash: {self.info_hash})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

