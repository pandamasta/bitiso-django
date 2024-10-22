import os
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError

@deconstructible
class PathAndRename:
    """
    Utility class to rename file uploads with a unique identifier.
    """
    def __init__(self, sub_path):
        # Store the subdirectory where files will be uploaded
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        """
        Generates a unique filename using UUID, preserving the original file extension.
        """
        ext = filename.split('.')[-1]  # Get the file extension (e.g., jpg, png)
        # Create a unique filename using UUID
        unique_filename = f"{uuid4().hex}.{ext}"
        # Return the full path where the file will be uploaded
        return os.path.join(self.sub_path, unique_filename)


def validate_image_type(image):
    """
    Validator to ensure only allowed image types (JPEG, PNG) are uploaded.
    """
    allowed_types = ['image/jpeg', 'image/png']
    if image.file.content_type not in allowed_types:
        raise ValidationError('Unsupported file type. Allowed types: JPEG, PNG.')

def validate_file_size(image):
    """
    Validator to ensure the uploaded file is within the allowed size limit.
    """
    max_size_kb = 500  # Set max size to 500 KB
    if image.size > max_size_kb * 1024:
        raise ValidationError(f"Image file too large ( > {max_size_kb} KB )")
    
