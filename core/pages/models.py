 # pages/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class Page(models.Model):

    RESERVED_SLUGS = ['accounts', 'admin', 'login', 'logout', 'register']  # To pages/x app name conflict

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

    # Clean message avoid trigger crap error
    def clean(self):
        # Check if the slug is reserved
        if self.slug in self.RESERVED_SLUGS:
            raise ValidationError({
                'slug': _("The slug '%(slug)s' is reserved and cannot be used.") % {'slug': self.slug}
            })

    def save(self, *args, **kwargs):
        # Ensure the page is valid before saving
        self.clean()  # This ensures the clean method runs before saving

        # Ensure only one page is marked as homepage
        if self.is_homepage:
            Page.objects.filter(is_homepage=True).update(is_homepage=False)

        # Validate slug before saving
        if self.slug in self.RESERVED_SLUGS:
            raise ValidationError(f"The slug '{self.slug}' is reserved and cannot be used.")

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

