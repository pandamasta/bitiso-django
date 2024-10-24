# bitiso_user_profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BitisoUserProfile

User = get_user_model()

# Automatically create a BitisoUserProfile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        BitisoUserProfile.objects.create(user=instance)

# Ensure the profile is saved whenever the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure that the profile exists before trying to save it
    if hasattr(instance, 'bitisouserprofile'):
        instance.bitisouserprofile.save()


