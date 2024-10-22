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

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        # Check if an instance already exists in the database
        try:
            old_instance = UserProfile.objects.get(pk=self.pk)
            # Check if the new profile_picture is different from the existing one
            if old_instance.profile_picture and old_instance.profile_picture != self.profile_picture:
                # If the profile_picture is changing, delete the old one
                old_instance.profile_picture.delete(save=False)
        except UserProfile.DoesNotExist:
            # No old instance exists, so nothing to delete
            pass

        # Call the original save method to save the new profile picture
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the profile picture file when the UserProfile instance is deleted
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        super().delete(*args, **kwargs)