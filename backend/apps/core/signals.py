"""
Django signals for NewsHub application.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from apps.news.models import Article, Category, Comment
from apps.core.utils import generate_unique_slug


@receiver(pre_save, sender=Article)
def auto_generate_article_slug(sender, instance, **kwargs):
    """
    Automatically generate a unique slug for articles if not provided.
    
    Args:
        sender: The model class (Article)
        instance: The article instance being saved
        kwargs: Additional keyword arguments
    """
    if not instance.slug:
        instance.slug = generate_unique_slug(instance, instance.title)


@receiver(pre_save, sender=Category)
def auto_generate_category_slug(sender, instance, **kwargs):
    """
    Automatically generate a unique slug for categories if not provided.
    
    Args:
        sender: The model class (Category)
        instance: The category instance being saved
        kwargs: Additional keyword arguments
    """
    if not instance.slug:
        instance.slug = generate_unique_slug(instance, instance.name)


@receiver(post_save, sender=Article)
def update_category_article_count_on_create(sender, instance, created, **kwargs):
    """
    Update the article count for the category when an article is created or updated.
    
    Args:
        sender: The model class (Article)
        instance: The article instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    if instance.category:
        # Update article count for the category
        update_category_count(instance.category)
    
    # If the category was changed, update the old category too
    if not created and hasattr(instance, '_old_category_id'):
        if instance._old_category_id and instance._old_category_id != instance.category_id:
            try:
                old_category = Category.objects.get(pk=instance._old_category_id)
                update_category_count(old_category)
            except Category.DoesNotExist:
                pass


@receiver(pre_save, sender=Article)
def track_category_change(sender, instance, **kwargs):
    """
    Track if the category is being changed to update both old and new categories.
    
    Args:
        sender: The model class (Article)
        instance: The article instance being saved
        kwargs: Additional keyword arguments
    """
    if instance.pk:
        try:
            old_instance = Article.objects.get(pk=instance.pk)
            instance._old_category_id = old_instance.category_id
        except Article.DoesNotExist:
            instance._old_category_id = None
    else:
        instance._old_category_id = None


@receiver(post_delete, sender=Article)
def update_category_article_count_on_delete(sender, instance, **kwargs):
    """
    Update the article count for the category when an article is deleted.
    
    Args:
        sender: The model class (Article)
        instance: The article instance that was deleted
        kwargs: Additional keyword arguments
    """
    if instance.category:
        update_category_count(instance.category)


def update_category_count(category):
    """
    Update the article count for a category.
    
    Args:
        category: The Category instance to update
    """
    # Count only published articles
    count = Article.objects.filter(
        category=category,
        status='published'
    ).count()
    
    # Update the category's article_count field
    Category.objects.filter(pk=category.pk).update(article_count=count)


@receiver(post_save, sender=Comment)
def update_article_comment_count(sender, instance, created, **kwargs):
    """
    Update the article when a comment is added.
    
    This can be extended to maintain a comment count on the Article model.
    
    Args:
        sender: The model class (Comment)
        instance: The comment instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    if created and instance.is_approved:
        # Optionally: send notification to article author
        pass


@receiver(post_delete, sender=Comment)
def handle_comment_deletion(sender, instance, **kwargs):
    """
    Handle cleanup when a comment is deleted.
    
    Args:
        sender: The model class (Comment)
        instance: The comment instance that was deleted
        kwargs: Additional keyword arguments
    """
    # Optionally: update article comment count or other related data
    pass
