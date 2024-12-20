from django.db import models
from django.utils.translation import gettext_lazy as _

class License(models.Model):
    """
    License model to define various open-source licenses.
    """
    name = models.CharField(_("License name"), max_length=100)
    description = models.TextField(_("License description"), blank=True, default='')
    website_url = models.URLField(_("Official website URL"), max_length=2000, blank=True, null=True)

    class Meta:
        verbose_name = _("License")
        verbose_name_plural = _("Licenses")
        ordering = ['name']

    def __str__(self):
        return self.name

