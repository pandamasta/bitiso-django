# models/category.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from ..utils.slug_utils import generate_unique_slug

class Category(models.Model):
    """
    Category of torrents.
    """
    name = models.CharField(_("Name"), max_length=64, null=False)
    slug = models.SlugField(blank=True, null=True)
    category_parent_id = models.ForeignKey(
        'self', 
        verbose_name=_("Parent category"), 
        blank=True, 
        null=True,
        on_delete=models.PROTECT,
        related_name='children'
    )
    creation = models.DateTimeField(auto_now_add=True, null=False)
    deletion = models.DateTimeField(_("Delete?"), blank=True, null=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.category_parent_id.name} -> {self.name}" if self.category_parent_id else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
