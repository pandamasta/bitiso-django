# models/torrent.py

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
    name = models.CharField(_("Name"), max_length=128, null=False)
    slug = models.SlugField(blank=True, null=True)
    size = models.PositiveBigIntegerField(_("Size"), null=False, default=0)
    pieces = models.IntegerField(_("Number of pieces"), null=False, default=1)
    piece_size = models.IntegerField(_("Piece size in bytes"), null=False, default=0)
    magnet = models.TextField(_("Magnet URI"), null=False, default="NONAME")
    torrent_filename = models.CharField(_("Torrent file name"), max_length=128, null=False, default="NONAME")
    comment = models.CharField(_("Comment"), max_length=256, null=False, default="NONAME")
    trackers = models.ManyToManyField('Tracker', through="TrackerStat")
    file_list = models.TextField(_("List of files"), null=False, default="NONAME")
    file_nbr = models.IntegerField(_("Number of files"), null=False, default=1)

    # Other descriptive fields
    category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_("Show in the front end"), null=False, default=False)
    is_bitiso = models.BooleanField(_("Created by bitiso?"), null=False, default=True)
    description = models.TextField(_("Description"), blank=True, null=True, default='')
    website_url = models.CharField(_("URL of official website"), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_("URL of official download page"), max_length=2000, blank=True)
    website_url_repo = models.CharField(_("URL of repository"), max_length=2000, blank=True)
    version = models.CharField(_("Version of the software"), max_length=16, blank=True)
    gpg_signature = models.FileField(upload_to='torrent/', blank=True)
    metainfo_file = models.FileField(upload_to='torrent/', blank=True)
    hash_signature = models.CharField(_("Any hash signature"), max_length=128, blank=True, null=True)

    creation = models.DateTimeField(auto_now_add=True)
    deletion = models.DateTimeField(_("Delete?"), blank=True, null=True)
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Uploader',
        null=True,
        blank=True,
        default='',
        on_delete=models.PROTECT
    )

    # Stats
    seed = models.IntegerField(_("Number of seeds"), default=0)
    leech = models.IntegerField(_("Number of leeches"), default=0)
    dl_number = models.IntegerField(_("Number of downloads"), default=0)
    dl_completed = models.IntegerField(_("Number of completions"), default=0)

    # Project
    project = models.ForeignKey(Project, verbose_name='Project', null=True, on_delete=models.PROTECT, related_name='torrents')

    class Meta:
        verbose_name = _("Torrent")
        verbose_name_plural = _("Torrents")

    def __str__(self):
        return f"{self.name} (Hash {self.info_hash})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
