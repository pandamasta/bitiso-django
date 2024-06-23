import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Project

@receiver(post_delete, sender=Project)
def delete_project_images_on_delete(sender, instance, **kwargs):
    image_fields = ['mini_image', 'small_image', 'medium_image', 'large_image', 'image']
    for image_field in image_fields:
        image = getattr(instance, image_field)
        if image and os.path.isfile(image.path):
            os.remove(image.path)

