import os
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError

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




def resize_images_for_instance(instance, image_field_name, sizes):
    """
    Resize an image for a model instance into different sizes and save the new image paths.
    
    Args:
        instance: The model instance (e.g., Project).
        image_field_name: The name of the ImageField on the model (e.g., 'image').
        sizes: A dictionary of sizes. Keys are size names, and values are tuples (width, height).

    """
    image_field = getattr(instance, image_field_name, None)
    
    # Check if the image field exists and if there's an image
    if not image_field or not image_field.name:
        return
    
    try:
        img = Image.open(image_field.path)
    except (FileNotFoundError, ValueError) as e:
        raise ValidationError(f"Could not process the image: {e}")

    filename = os.path.basename(image_field.name)
    
    for size_name, size in sizes.items():
        img_copy = img.copy()  # Make a copy of the image to avoid modifying the original
        img_copy.thumbnail(size)
        
        # Define new path
        new_path_relative = f'img/{instance._meta.model_name}/{size_name}/{filename}'
        new_path_absolute = os.path.join(settings.MEDIA_ROOT, new_path_relative)

        # Ensure directory exists
        os.makedirs(os.path.dirname(new_path_absolute), exist_ok=True)

        # Save resized image
        img_copy.save(new_path_absolute)

        # Set the new path to the resized image field
        setattr(instance, f'{size_name}_image', new_path_relative)

    # Save the updated fields in the model
    instance.save(update_fields=[f'{size_name}_image' for size_name in sizes])
