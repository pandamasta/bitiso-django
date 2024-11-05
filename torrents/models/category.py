#torrents/models/category.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from ..utils.slug_utils import generate_unique_slug
from django.conf import settings

class Category(models.Model):
    """
    Category for organizing projects and torrents.
    """
    name = models.CharField(_("Name"), max_length=64)
    slug = models.SlugField(blank=True, null=True, unique=True)
    description = models.TextField(_("Description"), blank=True, default='') 
    parent_category = models.ForeignKey(
        'self',
        verbose_name=_("Parent category"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='children'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories', null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(_("Deleted at"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return f"{self.parent_category.name} -> {self.name}" if self.parent_category else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
