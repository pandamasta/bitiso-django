import os
from PIL import Image
from django.conf import settings

def resize_project_images(project):
    """
    Resizes the project's images into different sizes and updates the project model.
    """
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

    # Save the updated image paths in the model
    project.save(update_fields=['mini_image', 'small_image', 'medium_image', 'large_image'])
