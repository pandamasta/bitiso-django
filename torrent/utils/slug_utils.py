# utils/slug_utils.py
from django.utils.text import slugify

def generate_unique_slug(instance, value, slug_field_name='slug'):
    """
    Generate a unique slug for any model.
    """
    slug_candidate = slugify(value)
    unique_slug = slug_candidate
    model_class = instance.__class__
    number = 1
    while model_class.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug_candidate}-{number}"
        number += 1
    return unique_slug
