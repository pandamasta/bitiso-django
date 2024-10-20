# user_profiles/admin.py
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'get_is_active', 'get_username_last_changed')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = 'Is Active'

    def get_username_last_changed(self, obj):
        return obj.user.username_last_changed
    get_username_last_changed.short_description = 'Username Last Changed'
