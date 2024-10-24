from django.contrib import admin
from .models import BitisoUserProfile  # Ensure the model is correctly imported

@admin.register(BitisoUserProfile)
class BitisoUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_picture')
