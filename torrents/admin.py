from django.contrib import admin
from .models import Torrent, Category, Project, Tracker, TrackerStat, License

@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',  'file_count', 'is_active', 'status', 'torrent_file', 'project', 'category', 'created_at')
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('is_active', 'status', 'category')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    # Make certain fields read-only to prevent editing
    readonly_fields = ('info_hash', 'size', 'pieces', 'file_count', 'piece_size', 
                       'torrent_file', 'created_at', 'updated_at')

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
    """
    Custom admin configuration for Project model.
    """
    list_display = (
        'name','small_image_tag', 'is_active', 'torrent_count', 
        'description', 'category', 'license',
        'website_url', 'website_url_download', 'website_url_repo',
        'user', 'created_at'
    )
    search_fields = ('name', 'user__username')
    list_filter = ('is_active',)
    ordering = ('-created_at',)

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','website_url')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('url', 'last_seen','is_reachable', 'is_scrapable', 'is_reachable_mode', 'is_scrapable_mode')
    list_filter = ('is_reachable', 'is_reachable_mode', 'is_scrapable', 'is_scrapable_mode')
    search_fields = ('url',)

@admin.register(TrackerStat)
class TrackerStatAdmin(admin.ModelAdmin):
    list_display = ('torrent', 'tracker', 'announce_priority','seed', 'leech', 'complete','last_scrape_attempt','last_successful_scrape')
    search_fields = ('torrent__name', 'tracker__url')
    ordering = ('torrent',)

