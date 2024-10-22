# core/user_profiles/apps.py
from django.apps import AppConfig

class UserProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user_profiles'

    def ready(self):
        import core.user_profiles.signals  # Import the signals here
