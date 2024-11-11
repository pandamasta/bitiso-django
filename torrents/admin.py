from django.contrib import admin
from .models import Torrent, Category, Project, Tracker, TrackerStat

@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',  'file_count', 'is_active', 'status', 'category', 'created_at')
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('is_active', 'status', 'category')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Make certain fields read-only to prevent editing
    readonly_fields = ('info_hash', 'size', 'pieces', 'file_count', 'piece_size', 
                       'torrent_file_path', 'created_at', 'updated_at')

    # Optionally exclude fields if they should not appear in the admin form at all
    exclude = ('magnet',)  # Example if you need to exclude fields entirely

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent_category', 'created_at')  # Fixed the field names
    search_fields = ('name', 'parent_category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'user', 'created_at')  # Replace 'creation' with 'created_at'
    search_fields = ('name', 'user__username')
    list_filter = ('is_active',)
    ordering = ('-created_at',)  # Replace 'creation' with 'created_at'


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('url',)
    search_fields = ('url',)
    ordering = ('url',)

@admin.register(TrackerStat)
class TrackerStatAdmin(admin.ModelAdmin):
    list_display = ('torrent', 'tracker', 'seed', 'leech', 'complete')
    search_fields = ('torrent__name', 'tracker__url')
    ordering = ('torrent',)

