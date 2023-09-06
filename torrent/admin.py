from django.contrib import admin
from django import forms
from .models import *

from django.core.management import call_command

@admin.action(description='Show torrent in frontend')
def make_published(modeladmin, request, queryset):
    queryset.update(is_active=True)

class TrackerStatInline(admin.TabularInline):
    model = TrackerStat
    extra = 1

class TorrentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_bitiso', 'seed','leech', 'pieces', 'piece_size','metainfo_file']
    actions = [make_published]
    inlines = [TrackerStatInline]

class TrackerAdmin(admin.ModelAdmin):
    list_display = ['url']
    actions = [make_published]

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','description','small_image']
    actions = [make_published]

class CategoryAdmin(admin.ModelAdmin):
    ordering = ['category_parent_id', 'name']
    list_display = ['name', 'category_parent_id']
    list_filter = ['category_parent_id']



#############################

class ExternalTorrentAdminForm(forms.ModelForm):

    class Meta:
        model = ExternalTorrent
        fields = '__all__'


class ExternalTorrentAdmin(admin.ModelAdmin):
    form = ExternalTorrentAdminForm
    actions = ['download_torrent']

    def __str__(self):
        return self.url

    def download_torrent(self, request, queryset):

        print("In download_torrent")
        for obj in queryset:
            print(obj.url)
            call_command('download_torrent', obj.url)

    download_torrent.short_description = "Download torrent file"

admin.site.register(Project, ProjectAdmin)
admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(ExternalTorrent, ExternalTorrentAdmin)
admin.site.register(Category, CategoryAdmin)
