# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Custom User model to add extra fields
class CustomUser(AbstractUser):
    # Additional email field, set to be unique
    email = models.EmailField(_("email address"), unique=True)

    def __str__(self):
        return self.username
