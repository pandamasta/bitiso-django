from django.contrib import admin
from django import forms
from .models import *
from django.urls import path
from django.http import HttpResponseRedirect
from .forms import SetCategoryForm
from django.shortcuts import render

from django.core.management import call_command
from django.urls import reverse


@admin.action(description='Show torrent in frontend')
def make_published(modeladmin, request, queryset):
    queryset.update(is_active=True)

class TrackerStatInline(admin.TabularInline):
    model = TrackerStat
    extra = 1

class TorrentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_bitiso', 'seed','leech', 'pieces', 'piece_size','metainfo_file']
    actions = [make_published,'set_category']
    inlines = [TrackerStatInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('set-category/', self.admin_site.admin_view(self.set_category_view), name='set-category'),
        ]
        return custom_urls + urls


    @admin.action(description='Set torrent category')
    def set_category(self, request, queryset):
        selected = request.POST.getlist('_selected_action')
        url = reverse('admin:set-category') + '?ids=' + ','.join(selected)
        return HttpResponseRedirect(url)

    def set_category_view(self, request):
        ids = request.GET.get('ids')
        if request.method == 'POST':
            form = SetCategoryForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data['category']
                Torrent.objects.filter(id__in=ids.split(',')).update(category=category)
                self.message_user(request, "Category set successfully.")
                return HttpResponseRedirect('../')
        else:
            form = SetCategoryForm()

        context = dict(
           self.admin_site.each_context(request),
           form=form,
           title="Set Category for Torrents",
        )

        return render(request, "admin/set_category.html", context)


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
        self.ensure_directory_exists(settings.TORRENT_EXTERNAL)

        print("In download_torrent")
        for obj in queryset:
            print(obj.url)
            call_command('download_torrent', obj.url)

    download_torrent.short_description = "Download torrent file"
    @staticmethod
    def ensure_directory_exists(path):
        if not os.path.exists(path):
            os.makedirs(path)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Torrent, TorrentAdmin)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(ExternalTorrent, ExternalTorrentAdmin)
admin.site.register(Category, CategoryAdmin)
