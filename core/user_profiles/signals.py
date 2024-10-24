# user_profiles/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_abstract_user_profile(sender, instance, created, **kwargs):
    """This function is a placeholder for core logic, specific profile creation should be handled in project-specific apps."""
    # No logic here, leave profile creation for specific apps like bitiso_user_profiles
    pass

