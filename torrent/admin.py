from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(Tracker)

@admin.action(description='Show torrent in frontend')
def make_published(modeladmin, request, queryset):
    queryset.update(is_active=True)

class TorrentAdmin(admin.ModelAdmin):
    #list_display = ['name', 'is_ative', 'size', 'pieces', 'pieces_size','torrent_filename']
    list_display = ['name', 'seed','leech','is_active','size', 'pieces', 'piece_size','metainfo_file']
    actions = [make_published]

admin.site.register(Torrent, TorrentAdmin)
