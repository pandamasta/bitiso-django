from django.contrib import admin
from .models import Torrent, Category, Project, Tracker, TrackerStat

@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'size', 'file_count', 'is_active', 'category', 'created_at')  # Replace 'creation' with 'created_at'
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('is_active', 'category')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'  # Replace 'creation' with 'created_at'
    ordering = ('-created_at',)  # Replace 'creation' with 'created_at'

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

