import os
from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def resize_and_save_images(instance, image_field_name, sizes, base_path=None):
    """
    Generic function to resize images for any model instance and save them with specified paths.

    Args:
        instance: The model instance (e.g., Project or UserProfile).
        image_field_name: The name of the ImageField on the model to be resized (e.g., 'image').
        sizes: A dictionary where keys are size names and values are (width, height) tuples.
        base_path: Optional base path for storing images; defaults to 'img/{model_name}'.
    """
    image_field = getattr(instance, image_field_name, None)
    if not image_field or not image_field.name:
        logger.warning(f"No image found in field '{image_field_name}' for {instance}. Aborting resizing.")
        return

    # Determine base directory path (e.g., 'img/profile' or 'img/project')
    model_name = instance._meta.model_name
    base_path = base_path or f'img/{model_name}'

    # Open the original image
    try:
        img = Image.open(image_field.path)
        logger.debug(f"Opened image {image_field.path} for resizing.")
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.error(f"Could not process the image: {e}")
        raise ValidationError(f"Could not process the image: {e}")

    # Check if the image has an alpha channel
    is_transparent = img.mode == 'RGBA'

    # Get filename and extension
    filename, _ = os.path.splitext(os.path.basename(image_field.name))
    updated_fields = {}

    for size_name, size in sizes.items():
        img_copy = img.copy()
        img_copy.thumbnail(size)

        # Set format based on transparency
        if is_transparent:
            new_ext = '.png'
            save_format = 'PNG'
        else:
            new_ext = '.jpg'
            save_format = 'JPEG'

        # Define new filename with size and extension
        new_filename = f"{filename}_{size_name}{new_ext}"
        new_path_relative = f"{base_path}/{size_name}/{new_filename}"
        new_path_absolute = os.path.join(settings.MEDIA_ROOT, new_path_relative)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(new_path_absolute), exist_ok=True)

        # Save the resized image with appropriate format
        img_copy.save(new_path_absolute, format=save_format, quality=85 if save_format == 'JPEG' else None)
        logger.debug(f"Saved resized image {size_name} as {new_filename} in {save_format} format")

        # Update instance field dynamically
        resized_field_name = f"{size_name}_{image_field_name}"
        updated_fields[resized_field_name] = new_path_relative

    # Update model instance fields without triggering save()
    instance.__class__.objects.filter(pk=instance.pk).update(**updated_fields)
    logger.debug(f"Resized images saved for {instance._meta.verbose_name}: {instance}")
