#torrents/models/project.py

import logging
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..utils.image_utils import resize_images_for_instance
from ..utils.slug_utils import generate_unique_slug
from PIL import Image, UnidentifiedImageError
import os 
from core.utils import resize_and_save_images
from ..models.category import Category
from ..models.license import License
from django.utils.html import format_html

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



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
    category = models.ForeignKey(Category, verbose_name=_("Category"), null=True, on_delete=models.PROTECT)  # Assign category at project level
    license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Default license"))
    torrent_count = models.PositiveIntegerField(default=0, verbose_name="Number of Torrents")  
    
    # Image fields
    image = models.ImageField(upload_to='img/project/original/', null=True, blank=True, default='')
    mini_image = models.ImageField(upload_to='img/project/mini/', blank=True, default='')
    small_image = models.ImageField(upload_to='img/project/small/', blank=True, default='')
    medium_image = models.ImageField(upload_to='img/project/medium/', blank=True, default='')
    large_image = models.ImageField(upload_to='img/project/large/', blank=True, default='')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects', blank=True, null=True)
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
        logger.debug(f"Saving project: {self.name}")

        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)

        super().save(*args, **kwargs)  # Save model first to access image file path

        if self.image:
            resize_and_save_images(self, 'image', {
                'mini': (13, 13),
                'small': (40, 40),
                'medium': (150, 150),
                'large': (300, 300),
            })

    def delete(self, *args, **kwargs):
        """
        Deletes associated image files from the disk when the project is deleted.
        """
        image_fields = ['image', 'mini_image', 'small_image', 'medium_image', 'large_image']
        for field in image_fields:
            image_field = getattr(self, field, None)
            if image_field and image_field.name:
                file_path = image_field.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted {field} file at {file_path}")
        
        super().delete(*args, **kwargs)  # Call the parent class's delete method
        
    def small_image_tag(self):
        """
        Returns an HTML img tag for the small image, to be displayed in the admin interface.
        """
        if self.small_image:
            return format_html('<img src="{}" width="40" height="40" />', self.small_image.url)
        return "No Image"

    small_image_tag.short_description = "Small Image"  # Column header in admin
