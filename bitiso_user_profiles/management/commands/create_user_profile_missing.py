from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bitiso_user_profiles.models import BitisoUserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing user profiles'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(bitisouserprofile__isnull=True)
        for user in users_without_profiles:
            BitisoUserProfile.objects.create(user=user)
            self.stdout.write(f"Created profile for {user.username}")
        self.stdout.write(self.style.SUCCESS('Successfully created missing profiles'))

