"""
Core utility functions for NewsHub application.
"""
import os
import uuid
from typing import Optional
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q


def generate_unique_slug(instance, text: str, slug_field: str = 'slug') -> str:
    """
    Generate a unique slug for a model instance.
    
    Args:
        instance: The model instance (can be unsaved)
        text: The text to slugify (usually the title)
        slug_field: The name of the slug field (default: 'slug')
    
    Returns:
        A unique slug string
    """
    base_slug = slugify(text)
    unique_slug = base_slug
    model_class = instance.__class__
    counter = 1
    
    # Get the queryset, excluding the current instance if it has a pk
    if instance.pk:
        queryset = model_class.objects.exclude(pk=instance.pk)
    else:
        queryset = model_class.objects.all()
    
    # Keep incrementing counter until we find a unique slug
    while queryset.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
    
    return unique_slug


def get_upload_path(instance, filename: str, folder: str) -> str:
    """
    Generate upload path for media files with unique filename.
    
    Args:
        instance: The model instance
        filename: Original filename
        folder: The folder name (e.g., 'articles', 'authors', 'categories')
    
    Returns:
        Upload path string
    """
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Return path: folder/YYYY/MM/unique_filename.ext
    from datetime import datetime
    now = datetime.now()
    return os.path.join(folder, str(now.year), str(now.month).zfill(2), unique_filename)


def article_image_upload_path(instance, filename: str) -> str:
    """Upload path for article featured images."""
    return get_upload_path(instance, filename, 'articles')


def author_image_upload_path(instance, filename: str) -> str:
    """Upload path for author profile images."""
    return get_upload_path(instance, filename, 'authors')


def category_icon_upload_path(instance, filename: str) -> str:
    """Upload path for category icons."""
    return get_upload_path(instance, filename, 'categories')


def site_logo_upload_path(instance, filename: str) -> str:
    """Upload path for site logo images."""
    return get_upload_path(instance, filename, 'site/logos')


def site_favicon_upload_path(instance, filename: str) -> str:
    """Upload path for site favicon images."""
    return get_upload_path(instance, filename, 'site/favicons')


def ad_banner_upload_path(instance, filename: str) -> str:
    """Upload path for advertisement banner images."""
    return get_upload_path(instance, filename, 'ads')


def homepage_section_upload_path(instance, filename: str) -> str:
    """Upload path for homepage section images."""
    return get_upload_path(instance, filename, 'homepage')


def validate_image_file(file: InMemoryUploadedFile, max_size_mb: int = 5) -> tuple[bool, Optional[str]]:
    """
    Validate an uploaded image file.
    
    Args:
        file: The uploaded file object
        max_size_mb: Maximum allowed file size in MB
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check file extension
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ext = file.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    # Check content type
    allowed_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_content_types:
        return False, "Invalid image content type"
    
    return True, None


def build_search_query(search_term: str, fields: list[str]) -> Q:
    """
    Build a Django Q object for searching across multiple fields.
    
    Args:
        search_term: The search term to query
        fields: List of field names to search in
    
    Returns:
        A Django Q object for filtering
    """
    query = Q()
    
    if not search_term:
        return query
    
    # Split search term into words
    words = search_term.split()
    
    # Build OR query across all fields for each word
    for word in words:
        word_query = Q()
        for field in fields:
            word_query |= Q(**{f"{field}__icontains": word})
        query &= word_query
    
    return query


def get_search_results(queryset, search_term: str, fields: list[str]):
    """
    Apply search filtering to a queryset.
    
    Args:
        queryset: The initial queryset
        search_term: The search term
        fields: List of field names to search in
    
    Returns:
        Filtered queryset
    """
    if not search_term:
        return queryset
    
    search_query = build_search_query(search_term, fields)
    return queryset.filter(search_query).distinct()


def format_reading_time(word_count: int, words_per_minute: int = 200) -> str:
    """
    Calculate and format reading time for an article.
    
    Args:
        word_count: Number of words in the article
        words_per_minute: Average reading speed (default: 200)
    
    Returns:
        Formatted reading time string (e.g., "5 min read")
    """
    if word_count <= 0:
        return "Less than 1 min read"
    
    minutes = max(1, round(word_count / words_per_minute))
    
    if minutes == 1:
        return "1 min read"
    return f"{minutes} min read"


def truncate_text(text: str, max_length: int = 160, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding suffix if truncated.
    
    Args:
        text: The text to truncate
        max_length: Maximum length (default: 160)
        suffix: Suffix to add if truncated (default: "...")
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Try to break at a word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix
