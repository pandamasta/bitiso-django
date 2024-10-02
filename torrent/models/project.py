# models/project.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ..utils.slug_utils import generate_unique_slug
import os
from PIL import Image
from django.conf import settings

class Project(models.Model):
    """
    Project model for managing torrent projects.
    """
    name = models.CharField(_("Project name"), max_length=128, null=False)
    slug = models.SlugField(blank=True, null=True)
    is_active = models.BooleanField(_("Show in the front end"), null=False, default=False)
    description = models.TextField(_("Description of project"), blank=True, null=True, default='')
    website_url = models.CharField(_("URL of official website"), max_length=2000, blank=True, null=True)
    website_url_download = models.CharField(_("URL of official download page"), max_length=2000, blank=True)
    website_url_repo = models.CharField(_("URL of repository"), max_length=2000, blank=True)

    # Image fields
    image = models.ImageField(upload_to='img/project/original/', null=True, blank=True)
    mini_image = models.ImageField(upload_to='img/project/mini/', blank=True)
    small_image = models.ImageField(upload_to='img/project/small/', blank=True)
    medium_image = models.ImageField(upload_to='img/project/medium/', blank=True)
    large_image = models.ImageField(upload_to='img/project/large/', blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', default=1)
    creation = models.DateTimeField(auto_now_add=True)
    deletion = models.DateTimeField(_("Delete?"), blank=True, null=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)  # Save original image
        self.create_resized_images()

    def create_resized_images(self):
        if not self.image:
            return

        sizes = {
            'mini': (13, 13),
            'small': (40, 40),
            'medium': (150, 150),
            'large': (300, 300),
        }

        for size_name, size in sizes.items():
            img = Image.open(self.image.path)
            img.thumbnail(size)

            filename = os.path.basename(self.image.name)
            new_path_relative = f'img/project/{size_name}/{filename}'
            new_path_absolute = os.path.join(settings.MEDIA_ROOT, new_path_relative)

            os.makedirs(os.path.dirname(new_path_absolute), exist_ok=True)
            img.save(new_path_absolute)

            setattr(self, f'{size_name}_image', new_path_relative)

        super().save(update_fields=['mini_image', 'small_image', 'medium_image', 'large_image'])
