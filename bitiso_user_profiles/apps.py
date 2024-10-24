from django.apps import AppConfig


class BitisoUserProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bitiso_user_profiles'

    def ready(self):
        import bitiso_user_profiles.signals  # This ensures the signal is connected