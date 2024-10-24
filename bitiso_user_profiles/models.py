from django.db import models
from core.user_profiles.models import AbstractUserProfile
from django.conf import settings

class BitisoUserProfile(AbstractUserProfile):
    # Any additional fields related to BitisoUserProfile
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bitisouserprofile'  # This is key to accessing the profile
    )
    pass

