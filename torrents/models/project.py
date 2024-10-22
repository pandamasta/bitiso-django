#torrents/models/project.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from ..utils.slug_utils import generate_unique_slug
from ..utils.image_utils import resize_project_images  # Assuming you place the resizing logic here
from django.conf import settings

class Project(models.Model):
    """
    Project model for managing torrent projects.
    """
    name = models.CharField(_("Project name"), max_length=128)
    slug = models.SlugField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(_("Show in the front end"), default=False)
    description = models.TextField(_("Description of project"), blank=True, default='')
    website_url = models.URLField(_("Official website URL"), max_length=2000, blank=True, null=True)
    website_url_download = models.URLField(_("Download page URL"), max_length=2000, blank=True)
    website_url_repo = models.URLField(_("Repository URL"), max_length=2000, blank=True)

    # Image fields
    image = models.ImageField(upload_to='img/project/original/', null=True, blank=True)
    mini_image = models.ImageField(upload_to='img/project/mini/', blank=True)
    small_image = models.ImageField(upload_to='img/project/small/', blank=True)
    medium_image = models.ImageField(upload_to='img/project/medium/', blank=True)
    large_image = models.ImageField(upload_to='img/project/large/', blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(_("Deleted at"), blank=True, null=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)  # Save the model first

        # Call the utility function to handle resizing
        if self.image:
            resize_project_images(self)  # Pass the model instance to the utility function
