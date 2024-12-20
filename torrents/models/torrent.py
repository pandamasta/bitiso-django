#torrents/models/torrent.py

import os
import logging
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..models.category import Category
from ..models.project import Project
from ..models.license import License
from ..utils.slug_utils import generate_unique_slug
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Set up a logger for the application
logger = logging.getLogger(__name__)


from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

ARCHITECTURE_CHOICES = [
    ('i386', 'i386'),
    ('amd64', 'amd64'),
    ('arm64', 'ARM64'),
    ('arm', 'ARM'),
    ('other', 'Other'),

]

OS_CHOICES = [
    ('linux', 'Linux'),
    ('windows', 'Windows'),
    ('macos', 'MacOS'),
    ('android', 'Android'),
    ('bsd', 'BSD'),
]

# Status choices for torrent
STATUS_CHOICES = [
    ('active', _("Active - visible to all")),
    ('pending', _("Pending validation")),
    ('blocked', _("Blocked")),
    ('deleted', _("Deleted")),
]

class Torrent(models.Model):
    """
    Torrent data model.
    """
    info_hash = models.CharField(_("SHA1 of torrent"), max_length=40, unique=True)
    name = models.CharField(_("Name"), max_length=128)
    slug = models.SlugField(max_length=128, blank=True, null=True, unique=True)
    size = models.PositiveBigIntegerField(_("Size in bytes"), default=0)
    pieces = models.PositiveIntegerField(_("Number of pieces"), default=1)
    piece_size = models.PositiveIntegerField(_("Piece size in bytes"), default=0)
    magnet = models.TextField(_("Magnet URI"), blank=True, null=True)
    torrent_file = models.FileField(_("Torrent file"), upload_to="torrents/", blank=True, null=True)
    comment = models.CharField(_("Comment"), max_length=256, blank=True, null=True)
    trackers = models.ManyToManyField('Tracker', through="TrackerStat")
    file_list = models.TextField(_("List of files"), blank=True, null=True)
    file_count = models.PositiveIntegerField(_("Number of files"), default=1)

    # Optional fields for architecture and OS
    architecture = models.CharField(_("Architecture"), max_length=10, choices=ARCHITECTURE_CHOICES, blank=True, null=True)
    os = models.CharField(_("Operating System"), max_length=10, choices=OS_CHOICES, blank=True, null=True)

    # GPG Signature Path
    gpg_signature = models.FileField(_("GPG signature file"), upload_to="torrents/", blank=True, null=True)
    is_signed = models.BooleanField(_("Is signed"), default=False)

    # Descriptive fields
    category = models.ForeignKey('Category', verbose_name=_("Category"), null=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(_("Show in the front end"), default=False)
    is_bitiso = models.BooleanField(_("Created by Bitiso?"), default=True)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(_("Description"), blank=True, null=True)
    website_url = models.URLField(_("Official website URL"), max_length=2000, blank=True, null=True)
    website_url_download = models.URLField(_("Download page URL"), max_length=2000, blank=True, null=True)
    website_url_repo = models.URLField(_("Repository URL"), max_length=2000, blank=True, null=True)
    version = models.CharField(_("Version of the software"), max_length=32, blank=True, null=True)
    license = models.ForeignKey(
        'License',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("License"),
        help_text=_("Overrides project license if specified")
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='torrents', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(_("Deleted at"), blank=True, null=True)
    # Statistics
    seed_count = models.PositiveIntegerField(_("Number of seeds"), default=0)
    leech_count = models.PositiveIntegerField(_("Number of leeches"), default=0)
    download_count = models.PositiveIntegerField(_("Number of downloads"), default=0)
    completion_count = models.PositiveIntegerField(_("Number of completions"), default=0)

    # Project relation
    project = models.ForeignKey('Project', verbose_name=_("Project"), null=True, on_delete=models.PROTECT, related_name='torrents')

    class Meta:
        verbose_name = _("Torrent")
        verbose_name_plural = _("Torrents")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['info_hash']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} (Hash: {self.info_hash})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name, keep_extension=True)  # Set to True or False as needed
        super().save(*args, **kwargs)

# Delete single or multiple .torrent file
@receiver(post_delete, sender=Torrent)
def delete_torrent_files(sender, instance, **kwargs):
    """
    Deletes associated files when a Torrent instance is deleted.
    """
    # Delete torrent file
    if instance.torrent_file:
        torrent_file_name = instance.torrent_file.name
        try:
            instance.torrent_file.delete(save=False)  # Use storage backend
            logger.info(f"Torrent file {torrent_file_name} deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete torrent file {torrent_file_name}: {e}")

    # Delete GPG signature file
    if instance.gpg_signature:
        gpg_signature_name = instance.gpg_signature.name
        try:
            instance.gpg_signature.delete(save=False)  # Use storage backend
            logger.info(f"GPG signature file {gpg_signature_name} deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete GPG signature file {gpg_signature_name}: {e}")
    
