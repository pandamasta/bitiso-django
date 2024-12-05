# utils/slug_utils.py
import re
from django.utils.text import slugify

import re
import os
from django.utils.text import slugify

def generate_unique_slug(instance, value, slug_field_name='slug', keep_extension=True):
    """
    Generate a unique slug for a model instance.
    If the value is a filename, optionally keep the file extension and ensure uniqueness.

    Args:
        instance: The model instance for which the slug is being generated.
        value (str): The input value to generate the slug from.
        slug_field_name (str): The name of the slug field in the model (default: 'slug').
        keep_extension (bool): Whether to keep the file extension in the slug (default: False).

    Returns:
        str: A unique slug.
    """
    # Extract the base name and extension if needed
    if keep_extension:
        base_name, extension = os.path.splitext(value)
        if extension:
            value = f"{base_name}-{extension.lstrip('.')}"  # Add extension to the slug-friendly name

    # Remove file extensions if not keeping them
    else:
        value = re.sub(r'\.[a-zA-Z0-9]+$', '', value)

    # Generate the initial slug
    slug_candidate = slugify(value)

    # Ensure the slug is unique
    unique_slug = slug_candidate
    model_class = instance.__class__
    number = 1

    while model_class.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug_candidate}-{number}"
        number += 1

    return unique_slug
