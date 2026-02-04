"""
Custom validators for NewsHub models.

This module provides validation functions for uploaded files,
ensuring proper file types, sizes, and formats for article images,
author profiles, and category icons.
"""
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import os


def validate_image_file_type(file: UploadedFile):
    """
    Validate that the uploaded file is a valid image.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If the file is not a valid image
    """
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ext = file.name.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid file extension. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Validate content type
    allowed_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(file, 'content_type') and file.content_type not in allowed_content_types:
        raise ValidationError(
            "Invalid image file. Please upload a valid image file."
        )
    
    # Try to open and verify the image using PIL
    try:
        img = Image.open(file)
        img.verify()
        # Reset file pointer after verification
        file.seek(0)
    except Exception:
        raise ValidationError(
            "Corrupted or invalid image file. Please upload a valid image."
        )


def validate_image_size(file: UploadedFile, max_size_mb: int = 5):
    """
    Validate that the uploaded image does not exceed the maximum size.
    
    Args:
        file: The uploaded file object
        max_size_mb: Maximum allowed file size in MB (default: 5)
    
    Raises:
        ValidationError: If the file size exceeds the limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f"File size exceeds the maximum limit of {max_size_mb}MB. "
            f"Current size: {file.size / (1024 * 1024):.2f}MB"
        )


def validate_image_dimensions(file: UploadedFile, min_width: int = 400, 
                               min_height: int = 300, max_width: int = 4000, 
                               max_height: int = 4000):
    """
    Validate image dimensions.
    
    Args:
        file: The uploaded file object
        min_width: Minimum width in pixels (default: 400)
        min_height: Minimum height in pixels (default: 300)
        max_width: Maximum width in pixels (default: 4000)
        max_height: Maximum height in pixels (default: 4000)
    
    Raises:
        ValidationError: If dimensions are out of acceptable range
    """
    try:
        img = Image.open(file)
        width, height = img.size
        file.seek(0)  # Reset file pointer
        
        if width < min_width or height < min_height:
            raise ValidationError(
                f"Image dimensions too small. Minimum: {min_width}x{min_height}px. "
                f"Uploaded: {width}x{height}px"
            )
        
        if width > max_width or height > max_height:
            raise ValidationError(
                f"Image dimensions too large. Maximum: {max_width}x{max_height}px. "
                f"Uploaded: {width}x{height}px"
            )
    except ValidationError:
        raise
    except Exception:
        raise ValidationError("Unable to read image dimensions.")


def validate_article_image(file: UploadedFile):
    """
    Comprehensive validation for article featured images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=5)
    validate_image_dimensions(file, min_width=800, min_height=450)


def validate_author_image(file: UploadedFile):
    """
    Comprehensive validation for author profile images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=2)
    validate_image_dimensions(file, min_width=200, min_height=200, 
                             max_width=2000, max_height=2000)


def validate_category_icon(file: UploadedFile):
    """
    Comprehensive validation for category icon images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=1)
    validate_image_dimensions(file, min_width=100, min_height=100,
                             max_width=1000, max_height=1000)


def validate_site_logo(file: UploadedFile):
    """
    Comprehensive validation for site logo images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=2)
    validate_image_dimensions(file, min_width=200, min_height=50,
                             max_width=1000, max_height=300)


def validate_favicon(file: UploadedFile):
    """
    Comprehensive validation for favicon images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=1)
    validate_image_dimensions(file, min_width=16, min_height=16,
                             max_width=512, max_height=512)


def validate_ad_banner(file: UploadedFile):
    """
    Comprehensive validation for advertisement banner images.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_size(file, max_size_mb=3)
    validate_image_dimensions(file, min_width=300, min_height=100,
                             max_width=2000, max_height=1000)


def validate_content_length(value: str, min_length: int = 100, max_length: int = 50000):
    """
    Validate the length of article content.
    
    Args:
        value: The content string
        min_length: Minimum required length (default: 100)
        max_length: Maximum allowed length (default: 50000)
    
    Raises:
        ValidationError: If content length is out of range
    """
    if not value:
        raise ValidationError("Content cannot be empty.")
    
    content_length = len(value.strip())
    
    if content_length < min_length:
        raise ValidationError(
            f"Content is too short. Minimum length: {min_length} characters. "
            f"Current length: {content_length} characters."
        )
    
    if content_length > max_length:
        raise ValidationError(
            f"Content is too long. Maximum length: {max_length} characters. "
            f"Current length: {content_length} characters."
        )


def validate_title_length(value: str, min_length: int = 10, max_length: int = 200):
    """
    Validate the length of article title.
    
    Args:
        value: The title string
        min_length: Minimum required length (default: 10)
        max_length: Maximum allowed length (default: 200)
    
    Raises:
        ValidationError: If title length is out of range
    """
    if not value:
        raise ValidationError("Title cannot be empty.")
    
    title_length = len(value.strip())
    
    if title_length < min_length:
        raise ValidationError(
            f"Title is too short. Minimum length: {min_length} characters. "
            f"Current length: {title_length} characters."
        )
    
    if title_length > max_length:
        raise ValidationError(
            f"Title is too long. Maximum length: {max_length} characters. "
            f"Current length: {title_length} characters."
        )


def validate_slug(value: str):
    """
    Validate that a slug contains only valid characters.
    
    Args:
        value: The slug string
    
    Raises:
        ValidationError: If slug contains invalid characters
    """
    import re
    
    if not value:
        raise ValidationError("Slug cannot be empty.")
    
    # Slug should only contain lowercase letters, numbers, and hyphens
    if not re.match(r'^[a-z0-9-]+$', value):
        raise ValidationError(
            "Slug can only contain lowercase letters, numbers, and hyphens."
        )
    
    if value.startswith('-') or value.endswith('-'):
        raise ValidationError("Slug cannot start or end with a hyphen.")
    
    if '--' in value:
        raise ValidationError("Slug cannot contain consecutive hyphens.")


def validate_hex_color(value: str):
    """
    Validate that a color string is in valid hex format.
    
    Args:
        value: The color string (e.g., #e74c3c or #e74)
    
    Raises:
        ValidationError: If color is not in valid hex format
    """
    import re
    
    if not value:
        raise ValidationError("Color value cannot be empty.")
    
    # Hex color format: #RGB or #RRGGBB
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(
            "Invalid hex color format. Use #RGB or #RRGGBB format (e.g., #e74c3c or #abc)."
        )
