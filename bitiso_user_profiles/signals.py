# bitiso_user_profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BitisoUserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a BitisoUserProfile when a new CustomUser is created.
    """
    if created:
        BitisoUserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure the BitisoUserProfile is saved whenever the CustomUser is saved.
    If the profile does not exist, create it.
    """
    # Check if the profile exists, create it if not
    if not hasattr(instance, 'bitisouserprofile'):
        BitisoUserProfile.objects.create(user=instance)
    else:
        instance.bitisouserprofile.save()