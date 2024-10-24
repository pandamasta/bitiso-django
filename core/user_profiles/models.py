from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .utils import PathAndRename, validate_image_type, validate_file_size  # Import validators

# Set the upload path using the utility class
profile_pic_upload_path = PathAndRename('profile_pics/')

class AbstractUserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(_("Bio"), blank=True)
    profile_picture = models.ImageField(
        _("Profile Picture"), 
        upload_to=profile_pic_upload_path, 
        validators=[validate_image_type, validate_file_size],  # Validators
        blank=True, 
        null=True
    )

    class Meta:
        abstract = True  # This makes the model abstract

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        # Check if an instance already exists in the database
        try:
            old_instance = type(self).objects.get(pk=self.pk)
            # Check if the profile picture is being changed
            if old_instance.profile_picture and old_instance.profile_picture != self.profile_picture:
                old_instance.profile_picture.delete(save=False)
        except type(self).DoesNotExist:
            # No old instance exists, so nothing to delete
            pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the profile picture file when the profile is deleted
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        super().delete(*args, **kwargs)
