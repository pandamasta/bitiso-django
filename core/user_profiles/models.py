from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .utils import PathAndRename, validate_image_type, validate_file_size  # Import validators

# Set the upload path using the utility class
profile_pic_upload_path = PathAndRename('profile_pics/')

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(_("Bio"), blank=True)
    profile_picture = models.ImageField(
        _("Profile Picture"), 
        upload_to=profile_pic_upload_path, 
        validators=[validate_image_type, validate_file_size],  # Use the validators here
        blank=True, 
        null=True
    )
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    social_links = models.JSONField(_("Social Links"), blank=True, null=True)
    privacy_settings = models.JSONField(_("Privacy Settings"), blank=True, null=True)
    notification_preferences = models.JSONField(_("Notification Preferences"), blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
