from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(_("Profile Picture"), upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(_("Bio"), blank=True)
    social_links = models.JSONField(_("Social Links"), blank=True, null=True)  # For links to social profiles
    privacy_settings = models.JSONField(_("Privacy Settings"), blank=True, null=True)
    notification_preferences = models.JSONField(_("Notification Preferences"), blank=True, null=True)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
