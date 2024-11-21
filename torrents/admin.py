from django.contrib import admin
from .models import Torrent, Category, Project, Tracker, TrackerStat, License

@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    """
    Admin interface for the Torrent model with GPG signature handling.
    """
    # Fields to display in the list view
    list_display = (
        'name', 'slug', 'file_count', 'is_active', 'status', 
        'torrent_file', 'gpg_signature_status', 'project', 
        'category', 'created_at', 'seed_count', 'leech_count', 'download_count'
    )
    # Searchable fields
    search_fields = ('name', 'slug', 'category__name', 'project__name', 'info_hash')
    # Filters for narrowing down the list
    list_filter = ('is_active', 'status', 'category', 'project', 'is_bitiso', 'is_signed')
    # Automatically generate slugs based on name
    prepopulated_fields = {'slug': ('name',)}
    # Add navigation hierarchy based on creation date
    date_hierarchy = 'created_at'
    # Default ordering
    ordering = ('-created_at',)
    
    # Read-only fields to prevent manual editing of computed or system fields
    readonly_fields = (
        'info_hash', 'size', 'pieces', 'file_count', 
        'piece_size', 'torrent_file', 'gpg_signature', 
        'created_at', 'updated_at', 'seed_count', 
        'leech_count', 'download_count', 'completion_count', 'is_signed'
    )
    
    # Display fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'version', 'status', 'is_active', 'is_bitiso')
        }),
        ('Relations', {
            'fields': ('project', 'category', 'license', 'user')
        }),
        ('Torrent Details', {
            'fields': ('info_hash', 'size', 'pieces', 'piece_size', 'file_count', 'torrent_file')
        }),
        ('GPG Signature', {
            'fields': ('gpg_signature', 'is_signed'),
            'description': "Manage the GPG signature and signed status of the torrent."
        }),
        ('Statistics', {
            'fields': ('seed_count', 'leech_count', 'download_count', 'completion_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    # Actions (e.g., bulk activation/deactivation)
    actions = ['activate_torrents', 'deactivate_torrents', 'mark_as_signed', 'mark_as_unsigned']

    def activate_torrents(self, request, queryset):
        """
        Admin action to activate selected torrents.
        """
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} torrents successfully activated.")
    activate_torrents.short_description = "Activate selected torrents"

    def deactivate_torrents(self, request, queryset):
        """
        Admin action to deactivate selected torrents.
        """
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} torrents successfully deactivated.")
    deactivate_torrents.short_description = "Deactivate selected torrents"

    def mark_as_signed(self, request, queryset):
        """
        Admin action to mark selected torrents as signed.
        """
        queryset.update(is_signed=True)
        self.message_user(request, f"{queryset.count()} torrents marked as signed.")
    mark_as_signed.short_description = "Mark selected torrents as signed"

    def mark_as_unsigned(self, request, queryset):
        """
        Admin action to mark selected torrents as unsigned.
        """
        queryset.update(is_signed=False)
        self.message_user(request, f"{queryset.count()} torrents marked as unsigned.")
    mark_as_unsigned.short_description = "Mark selected torrents as unsigned"

    def gpg_signature_status(self, obj):
        """
        Displays the status of the GPG signature in the admin list.
        """
        return "Signed" if obj.is_signed else "Unsigned"
    gpg_signature_status.short_description = "GPG Status"
    gpg_signature_status.admin_order_field = 'is_signed'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description','parent_category', 'created_at')  # Fixed the field names
    search_fields = ('name', 'parent_category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for the Project model with image upload and management.
    """
    # Fields to display in the list view
    list_display = (
        'name', 'small_image_tag', 'slug', 'is_active', 'category', 'license', 
        'user', 'torrent_count', 'website_url', 'created_at'
    )
    # Searchable fields
    search_fields = ('name', 'slug', 'category__name', 'user__username', 'license__name')
    # Filters for narrowing down the list
    list_filter = ('is_active', 'category', 'license')
    # Add navigation hierarchy based on creation date
    date_hierarchy = 'created_at'
    # Default ordering
    ordering = ('-created_at',)
    
    # Read-only fields to prevent manual editing of computed or system fields
    readonly_fields = ('small_image_tag', 'torrent_count', 'created_at', 'updated_at', 'deleted_at')
    
    # Display fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'category', 'license', 'user', 'image', 'small_image_tag')
        }),
        ('Related Data', {
            'fields': ('torrent_count',),
            'description': "Information about related torrents."
        }),
        ('Web Presence', {
            'fields': ('website_url', 'website_url_download', 'website_url_repo'),
        }),
        ('Timestamps', {
            'fields': ('slug', 'created_at', 'updated_at', 'deleted_at'),
        }),
    )
    
    # Actions for bulk operations
    actions = ['activate_projects', 'deactivate_projects']

    def activate_projects(self, request, queryset):
        """
        Admin action to activate selected projects.
        """
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} projects successfully activated.")
    activate_projects.short_description = "Activate selected projects"

    def deactivate_projects(self, request, queryset):
        """
        Admin action to deactivate selected projects.
        """
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} projects successfully deactivated.")
    deactivate_projects.short_description = "Deactivate selected projects"

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','website_url')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('url', 'last_seen','is_reachable', 'is_scrapable', 'is_reachable_mode', 'is_scrapable_mode','created_at')
    list_filter = ('is_reachable', 'is_reachable_mode', 'is_scrapable', 'is_scrapable_mode')
    search_fields = ('url',)

@admin.register(TrackerStat)
class TrackerStatAdmin(admin.ModelAdmin):
    list_display = ('torrent', 'tracker', 'announce_priority','seed', 'leech', 'complete','last_scrape_attempt','last_successful_scrape','created_at')
    search_fields = ('torrent__name', 'tracker__url')
    ordering = ('torrent',)

