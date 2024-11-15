# torrents/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models.category import Category
from .models.license import License
from .models.project import Project
from .models.torrent import Torrent

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(License)
class LicenseTranslationOptions(TranslationOptions):
    fields = ('description','website_url')

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(Torrent)
class TorrentTranslationOptions(TranslationOptions):
    fields = ('description',)
