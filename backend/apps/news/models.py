"""
News content management models for NewsHub.

This module contains models for managing news articles, categories, tags,
comments, breaking news, and newsletter subscriptions.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import Author
from ckeditor.fields import RichTextField
from apps.core.utils import generate_unique_slug, article_image_upload_path, category_icon_upload_path
from apps.core.validators import validate_article_image, validate_category_icon


class Category(models.Model):
    """
    Category model for organizing articles into different sections
    (e.g., Politics, Sports, Technology, Business).
    Supports hierarchical subcategories.
    """
    
    name = models.CharField(
        max_length=100,
        help_text='Category name'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text='URL-friendly version of name (auto-generated)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        blank=True,
        null=True,
        help_text='Parent category (leave blank for main category)'
    )
    icon = models.ImageField(
        upload_to=category_icon_upload_path,
        blank=True,
        null=True,
        validators=[validate_category_icon],
        help_text='Category icon image'
    )
    color = models.CharField(
        max_length=7,
        default='#3b82f6',
        help_text='Category color in hex format (e.g., #3b82f6)'
    )
    description = models.TextField(
        blank=True,
        help_text='Category description'
    )
    article_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Number of published articles in this category'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this category is active and visible'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        unique_together = [['parent', 'name']]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate unique slug from name if not provided"""
        if not self.slug:
            base_slug = self.name if not self.parent else f"{self.parent.name}-{self.name}"
            self.slug = generate_unique_slug(self, base_slug)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the frontend URL for this category"""
        return f'/categories/{self.slug}/'
    
    def get_all_subcategories(self):
        """Recursively get all subcategories"""
        subcats = list(self.subcategories.filter(is_active=True))
        for subcat in list(subcats):
            subcats.extend(subcat.get_all_subcategories())
        return subcats


class Tag(models.Model):
    """
    Tag model for flexible article classification and filtering.
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Tag name'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text='URL-friendly version of name (auto-generated)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate unique slug from name if not provided"""
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """
    Article model representing news articles with rich metadata,
    relationships, and publication workflow.
    """
    
    class ArticleStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
    
    # Core content fields
    title = models.CharField(
        max_length=200,
        help_text='Article title'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text='URL-friendly version of title (auto-generated)'
    )
    summary = models.TextField(
        max_length=500,
        help_text='Brief article summary or excerpt'
    )
    content = RichTextField(
        help_text='Full article content (supports rich text)'
    )
    featured_image = models.ImageField(
        upload_to=article_image_upload_path,
        blank=True,
        null=True,
        validators=[validate_article_image],
        help_text='Article featured/cover image'
    )
    
    # Relationship fields
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text='Article category'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,
        help_text='Article tags for classification'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        help_text='Article author'
    )
    
    # Status and feature flags
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        help_text='Publication status'
    )
    is_breaking = models.BooleanField(
        default=False,
        help_text='Mark as breaking news'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Feature on homepage'
    )
    
    # Metrics
    views_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of article views'
    )
    
    # Timestamps
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Publication date and time'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_breaking']),
            models.Index(fields=['-published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug and set published_at when status changes to PUBLISHED.
        """
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        
        # Auto-set published_at when status changes to PUBLISHED
        if self.status == self.ArticleStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Atomically increment the views count"""
        Article.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])
    
    def get_read_time(self):
        """Calculate estimated reading time in minutes (200 words/minute)"""
        word_count = len(self.content.split())
        read_time = word_count / 200
        return max(1, round(read_time))  # Minimum 1 minute
    
    @property
    def get_comment_count(self):
        """Get count of approved comments"""
        return self.comments.filter(is_approved=True).count()
    
    @property
    def is_published(self):
        """Check if article is published"""
        return self.status == self.ArticleStatus.PUBLISHED


class Comment(models.Model):
    """
    Comment model for article discussions with moderation support.
    """
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Article being commented on'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='User who posted the comment'
    )
    content = models.TextField(
        max_length=1000,
        help_text='Comment text'
    )
    is_approved = models.BooleanField(
        default=False,
        help_text='Moderator approval status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        article_title = self.article.title[:30]
        return f'{self.user.username} on "{article_title}..."'
    
    def approve(self):
        """Approve the comment for public display"""
        self.is_approved = True
        self.save()


class BreakingNews(models.Model):
    """
    Breaking news model for urgent announcements and alerts.
    """
    
    text = models.CharField(
        max_length=200,
        help_text='Breaking news text'
    )
    urgent = models.BooleanField(
        default=True,
        help_text='Mark as urgent (affects display style)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show this breaking news item'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Breaking News')
        verbose_name_plural = _('Breaking News')
    
    def __str__(self):
        return self.text[:50] + ('...' if len(self.text) > 50 else '')
    
    def get_time_display(self):
        """Return human-readable time difference"""
        from django.utils.timesince import timesince
        
        now = timezone.now()
        diff = now - self.created_at
        
        # Just now (less than 1 minute)
        if diff.total_seconds() < 60:
            return "Just now"
        
        # X mins ago (less than 1 hour)
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min{'s' if minutes != 1 else ''} ago"
        
        # X hours ago (less than 24 hours)
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        # Use Django's timesince for longer periods
        else:
            return f"{timesince(self.created_at, now)} ago"
    
    @classmethod
    def get_active_breaking_news(cls):
        """Get all active breaking news ordered by urgency and creation time"""
        return cls.objects.filter(is_active=True).order_by('-urgent', '-created_at')


class BreakingNewsBanner(BreakingNews):
    """
    Proxy model to represent breaking news banners in CMS or API references.
    This keeps compatibility with external naming expectations without
    introducing a separate database table.
    """

    class Meta:
        proxy = True
        verbose_name = _('Breaking News Banner')
        verbose_name_plural = _('Breaking News Banners')


class NewsletterSubscriber(models.Model):
    """
    Newsletter subscriber model for email subscription management.
    """
    
    email = models.EmailField(
        unique=True,
        help_text='Subscriber email address'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Subscription status'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when subscriber unsubscribed'
    )
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = _('Newsletter Subscriber')
        verbose_name_plural = _('Newsletter Subscribers')
    
    def __str__(self):
        return self.email
    
    def clean(self):
        """Validate email format"""
        super().clean()
        validator = EmailValidator()
        try:
            validator(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Enter a valid email address.'})
    
    def unsubscribe(self):
        """Unsubscribe user from newsletter"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def resubscribe(self):
        """Resubscribe user to newsletter"""
        self.is_active = True
        self.unsubscribed_at = None
        self.save()


class Video(models.Model):
    """
    Video model for managing video content on NewsHub.
    """
    
    title = models.CharField(
        max_length=300,
        help_text='Video title'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text='URL-friendly version of title (auto-generated)'
    )
    description = models.TextField(
        blank=True,
        help_text='Video description'
    )
    thumbnail = models.ImageField(
        upload_to=article_image_upload_path,
        blank=True,
        null=True,
        validators=[validate_article_image],
        help_text='Video thumbnail image'
    )
    video_url = models.URLField(
        max_length=500,
        help_text='YouTube, Vimeo, or other video URL'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        help_text='Video category'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        help_text='Video author/uploader'
    )
    duration = models.CharField(
        max_length=20,
        blank=True,
        default='00:00',
        help_text='Video duration (e.g., 12:45)'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of views'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Feature this video on homepage'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show/hide video'
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Publication date'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update date'
    )
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count = F('views_count') + 1
        self.save(update_fields=['views_count'])
