# pages/admin.py

from django.contrib import admin
from .models import Page
from modeltranslation.admin import TranslationAdmin

@admin.register(Page)
class PageAdmin(TranslationAdmin):
    """Admin configuration for the Page model with translation support."""
    list_display = ('title', 'slug', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

