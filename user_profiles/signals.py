# user_profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
from accounts.models import CustomUser  # Adjust import if needed

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile for every new CustomUser."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the CustomUser is saved."""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # If the UserProfile doesn't exist, create it
        UserProfile.objects.create(user=instance)

