# accounts/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # Additional email field, set to be unique
    email = models.EmailField(_("email address"), unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username_last_changed = models.DateTimeField(null=True, blank=True, default=timezone.now)

    def can_change_username(self):
        """Returns True if the user can change their username (once per week)."""
        if self.username_last_changed:
            return timezone.now() > self.username_last_changed + timedelta(weeks=1)
        return True

    def __str__(self):
        return self.username
    
