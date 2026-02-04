"""
Core CMS models for NewsHub site-wide content management.

This module contains models for managing site settings, social links,
advertisements, footer content, sidebar widgets, homepage sections, and SEO.
"""

from django.db import models
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .utils import (
    generate_unique_slug,
    site_logo_upload_path,
    site_favicon_upload_path,
    ad_banner_upload_path,
    homepage_section_upload_path
)
from .validators import validate_site_logo, validate_favicon, validate_ad_banner, validate_hex_color


class SiteSettings(models.Model):
    """
    Singleton model for global site settings and branding.
    Only one instance should exist.
    """
    
    site_name = models.CharField(
        max_length=100,
        default='NewsHub',
        help_text='Site name displayed in header and meta tags'
    )
    logo = models.ImageField(
        upload_to=site_logo_upload_path,
        blank=True,
        null=True,
        validators=[validate_site_logo],
        help_text='Site logo (recommended: 200x50 to 1000x300 px)'
    )
    favicon = models.ImageField(
        upload_to=site_favicon_upload_path,
        blank=True,
        null=True,
        validators=[validate_favicon],
        help_text='Site favicon (recommended: 32x32 or 64x64 px)'
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        help_text='Site description for meta tags and about section'
    )
    contact_email = models.EmailField(
        blank=True,
        help_text='Primary contact email address'
    )
    primary_color = models.CharField(
        max_length=7,
        default='#e74c3c',
        validators=[validate_hex_color],
        help_text='Primary brand color (hex format, e.g., #e74c3c)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return f"Site Settings: {self.site_name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of site settings"""
        pass
    
    @classmethod
    def load(cls):
        """Load or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SocialLink(models.Model):
    """
    Social media links for site footer and header.
    """
    
    class Platform(models.TextChoices):
        FACEBOOK = 'facebook', _('Facebook')
        TWITTER = 'twitter', _('Twitter')
        INSTAGRAM = 'instagram', _('Instagram')
        LINKEDIN = 'linkedin', _('LinkedIn')
        YOUTUBE = 'youtube', _('YouTube')
        TIKTOK = 'tiktok', _('TikTok')
        PINTEREST = 'pinterest', _('Pinterest')
        REDDIT = 'reddit', _('Reddit')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        TELEGRAM = 'telegram', _('Telegram')
    
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        unique=True,
        help_text='Social media platform'
    )
    url = models.URLField(
        max_length=500,
        help_text='Full URL to social media profile'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Icon class name (e.g., fab fa-facebook)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Display this social link'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'platform']
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')
    
    def __str__(self):
        return f"{self.get_platform_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-set icon class based on platform if not provided"""
        if not self.icon:
            icon_map = {
                'facebook': 'fab fa-facebook-f',
                'twitter': 'fab fa-twitter',
                'instagram': 'fab fa-instagram',
                'linkedin': 'fab fa-linkedin-in',
                'youtube': 'fab fa-youtube',
                'tiktok': 'fab fa-tiktok',
                'pinterest': 'fab fa-pinterest-p',
                'reddit': 'fab fa-reddit-alien',
                'whatsapp': 'fab fa-whatsapp',
                'telegram': 'fab fa-telegram-plane',
            }
            self.icon = icon_map.get(self.platform, 'fas fa-link')
        super().save(*args, **kwargs)


class AdvertisementBanner(models.Model):
    """
    Advertisement banners for various positions on the site.
    """
    
    class Position(models.TextChoices):
        HEADER = 'header', _('Header')
        SIDEBAR = 'sidebar', _('Sidebar')
        FOOTER = 'footer', _('Footer')
        HOMEPAGE = 'homepage', _('Homepage')
        ARTICLE_TOP = 'article_top', _('Article Top')
        ARTICLE_BOTTOM = 'article_bottom', _('Article Bottom')
    
    title = models.CharField(
        max_length=100,
        help_text='Internal title for admin reference'
    )
    image = models.ImageField(
        upload_to=ad_banner_upload_path,
        validators=[validate_ad_banner],
        help_text='Advertisement banner image'
    )
    link_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='URL to redirect when banner is clicked'
    )
    position = models.CharField(
        max_length=20,
        choices=Position.choices,
        help_text='Where to display this banner'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show this advertisement'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order within position (lower numbers first)'
    )
    impressions = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Number of times displayed'
    )
    clicks = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text='Number of clicks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'order', '-created_at']
        verbose_name = _('Advertisement Banner')
        verbose_name_plural = _('Advertisement Banners')
        indexes = [
            models.Index(fields=['position', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"
    
    @property
    def click_through_rate(self):
        """Calculate CTR percentage"""
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)


class FooterSettings(models.Model):
    """
    Singleton model for footer content and settings.
    """
    
    copyright_text = models.CharField(
        max_length=200,
        default='© 2024 NewsHub. All rights reserved.',
        help_text='Copyright text displayed in footer'
    )
    show_social = models.BooleanField(
        default=True,
        help_text='Display social media links in footer'
    )
    extra_links = models.JSONField(
        default=list,
        blank=True,
        help_text='Additional footer links as JSON array: [{"text": "Privacy", "url": "/privacy"}]'
    )
    about_text = models.TextField(
        max_length=500,
        blank=True,
        help_text='Brief about text for footer'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Footer Settings')
        verbose_name_plural = _('Footer Settings')
    
    def __str__(self):
        return "Footer Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern) and validate data"""
        self.pk = 1
        self.full_clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass
    
    @classmethod
    def load(cls):
        """Load or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def clean(self):
        """Validate extra_links JSON structure"""
        super().clean()
        if self.extra_links:
            if not isinstance(self.extra_links, list):
                raise ValidationError({'extra_links': 'Must be a JSON array'})
            for link in self.extra_links:
                if not isinstance(link, dict) or 'text' not in link or 'url' not in link:
                    raise ValidationError({
                        'extra_links': 'Each link must have "text" and "url" keys'
                    })


class SidebarWidget(models.Model):
    """
    Configurable sidebar widgets for dynamic content blocks.
    """
    
    title = models.CharField(
        max_length=100,
        help_text='Widget title displayed in sidebar'
    )
    content = models.TextField(
        help_text='Widget content (supports HTML)'
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show this widget'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = _('Sidebar Widget')
        verbose_name_plural = _('Sidebar Widgets')
    
    def __str__(self):
        return self.title


class HomepageSection(models.Model):
    """
    Configurable homepage sections for dynamic layout control.
    """
    
    class SectionType(models.TextChoices):
        HERO = 'hero', _('Hero Section')
        FEATURED = 'featured', _('Featured Articles')
        TRENDING = 'trending', _('Trending News')
        EDITORIAL = 'editorial', _('Editorial Picks')
        CATEGORY = 'category', _('Category Showcase')
        VIDEO = 'video', _('Video Section')
    
    section_type = models.CharField(
        max_length=20,
        choices=SectionType.choices,
        help_text='Type of homepage section'
    )
    title = models.CharField(
        max_length=100,
        help_text='Section title'
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text='Optional subtitle or description'
    )
    image = models.ImageField(
        upload_to=homepage_section_upload_path,
        blank=True,
        null=True,
        validators=[validate_ad_banner],
        help_text='Section background or featured image'
    )
    articles = models.ManyToManyField(
        'news.Article',
        related_name='homepage_sections',
        blank=True,
        help_text='Articles to display in this section'
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text='Display order on homepage (lower numbers first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show this section on homepage'
    )
    max_articles = models.PositiveIntegerField(
        default=6,
        help_text='Maximum number of articles to display'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = _('Homepage Section')
        verbose_name_plural = _('Homepage Sections')
        indexes = [
            models.Index(fields=['section_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"
    
    def get_articles(self):
        """Get published articles for this section, limited by max_articles"""
        return self.articles.filter(
            status='published'
        ).order_by('-published_at')[:self.max_articles]


class SEOSettings(models.Model):
    """
    Singleton model for default SEO meta tags and settings.
    """
    
    default_title = models.CharField(
        max_length=60,
        default='NewsHub - Latest News & Updates',
        help_text='Default page title (max 60 chars for SEO)'
    )
    default_description = models.TextField(
        max_length=160,
        default='Stay updated with the latest news, breaking stories, and in-depth analysis.',
        help_text='Default meta description (max 160 chars for SEO)'
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text='Default meta keywords (comma-separated)'
    )
    og_image = models.ImageField(
        upload_to='seo/',
        blank=True,
        null=True,
        help_text='Default Open Graph image for social sharing'
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Google Analytics tracking ID (e.g., G-XXXXXXXXXX)'
    )
    google_site_verification = models.CharField(
        max_length=100,
        blank=True,
        help_text='Google Search Console verification code'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Settings')
        verbose_name_plural = _('SEO Settings')
    
    def __str__(self):
        return "SEO Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass
    
    @classmethod
    def load(cls):
        """Load or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def clean(self):
        """Validate field lengths for SEO best practices"""
        super().clean()
        if len(self.default_title) > 60:
            raise ValidationError({
                'default_title': 'Title should be 60 characters or less for optimal SEO'
            })
        if len(self.default_description) > 160:
            raise ValidationError({
                'default_description': 'Description should be 160 characters or less for optimal SEO'
            })
