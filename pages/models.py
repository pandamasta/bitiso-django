# pages/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True)
    content = models.TextField(_("Content"))
    is_published = models.BooleanField(_("Is Published"), default=True)
    is_homepage = models.BooleanField(_("Is Homepage"), default=False)  # New field to mark as home page
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def save(self, *args, **kwargs):
        # Ensure only one page is marked as homepage
        if self.is_homepage:
            Page.objects.filter(is_homepage=True).update(is_homepage=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title