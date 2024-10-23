#torrents/models/project.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..utils.image_utils import resize_images_for_instance
from ..utils.slug_utils import generate_unique_slug


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
    # Add timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

        # Only resize if a new image was uploaded
        if self.image and self.image_has_changed():
            resize_images_for_instance(self, 'image', {
                'mini': (13, 13),
                'small': (40, 40),
                'medium': (150, 150),
                'large': (300, 300),
            })

    def image_has_changed(self):
        """
        Check if the image has been changed.
        """
        if not self.pk:  # New instance
            return True

        old_image = Project.objects.filter(pk=self.pk).values('image').first()
        return old_image and old_image['image'] != self.image.name
