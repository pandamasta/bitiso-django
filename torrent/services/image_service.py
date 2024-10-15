# services/image_service.py

from PIL import Image
import os
from django.conf import settings

class ImageService:
    def create_resized_images(self, project):
        """
        Create resized images for a project.
        """
        if not project.image:
            return

        sizes = {
            'mini': (13, 13),
            'small': (40, 40),
            'medium': (150, 150),
            'large': (300, 300),
        }

        for size_name, size in sizes.items():
            img = Image.open(project.image.path)
            img.thumbnail(size)

            filename = os.path.basename(project.image.name)
            new_path_relative = f'img/project/{size_name}/{filename}'
            new_path_absolute = os.path.join(settings.MEDIA_ROOT, new_path_relative)

            os.makedirs(os.path.dirname(new_path_absolute), exist_ok=True)
            img.save(new_path_absolute)

            setattr(project, f'{size_name}_image', new_path_relative)

        project.save(update_fields=['mini_image', 'small_image', 'medium_image', 'large_image'])
