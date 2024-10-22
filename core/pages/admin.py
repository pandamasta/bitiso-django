# pages/admin.py

from django.contrib import admin
from .models import Page
from modeltranslation.admin import TranslationAdmin

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'is_homepage')
    list_filter = ('is_published', 'is_homepage')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

