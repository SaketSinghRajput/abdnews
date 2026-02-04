"""
Serializers for NewsHub CMS content management.

This module provides DRF serializers for site-wide CMS models including
site settings, social links, advertisements, footer, sidebar, homepage sections, and SEO.
"""

from rest_framework import serializers
from apps.news.serializers import ArticleListSerializer
from .models import (
    SiteSettings, SocialLink, AdvertisementBanner,
    FooterSettings, SidebarWidget, HomepageSection, SEOSettings
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for global site settings and branding configuration."""
    
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'logo', 'logo_url', 'favicon',
            'favicon_url', 'description', 'contact_email',
            'primary_color', 'updated_at'
        ]
        read_only_fields = ['id', 'logo_url', 'favicon_url', 'updated_at']
    
    def get_logo_url(self, obj):
        """Return absolute URL for site logo."""
        if obj.logo:
            return obj.logo.url
        return None
    
    def get_favicon_url(self, obj):
        """Return absolute URL for site favicon."""
        if obj.favicon:
            return obj.favicon.url
        return None


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer for social media links with platform details."""
    
    platform_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialLink
        fields = [
            'id', 'platform', 'platform_display', 'url', 'icon',
            'is_active', 'order'
        ]
        read_only_fields = ['id', 'platform_display']
    
    def get_platform_display(self, obj):
        """Return human-readable platform name."""
        return obj.get_platform_display()


class AdvertisementBannerSerializer(serializers.ModelSerializer):
    """Serializer for advertisement banners with position and performance metrics."""
    
    image_url = serializers.SerializerMethodField()
    position_display = serializers.SerializerMethodField()
    click_through_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = AdvertisementBanner
        fields = [
            'id', 'title', 'image', 'image_url', 'link_url', 'position',
            'position_display', 'is_active', 'order', 'impressions', 'clicks',
            'click_through_rate', 'created_at'
        ]
        read_only_fields = [
            'id', 'image_url', 'position_display', 'impressions',
            'clicks', 'click_through_rate', 'created_at'
        ]
    
    def get_image_url(self, obj):
        """Return absolute URL for advertisement image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_position_display(self, obj):
        """Return human-readable position name."""
        return obj.get_position_display()
    
    def get_click_through_rate(self, obj):
        """Return calculated click-through rate."""
        return obj.click_through_rate


class FooterSettingsSerializer(serializers.ModelSerializer):
    """Serializer for footer settings with copyright and extra links."""
    
    parsed_extra_links = serializers.SerializerMethodField()
    
    class Meta:
        model = FooterSettings
        fields = [
            'id', 'copyright_text', 'show_social', 'extra_links',
            'parsed_extra_links', 'about_text', 'updated_at'
        ]
        read_only_fields = ['id', 'parsed_extra_links', 'updated_at']
    
    def get_parsed_extra_links(self, obj):
        """Return parsed extra links ensuring proper JSON structure."""
        if obj.extra_links:
            return obj.extra_links
        return []


class SidebarWidgetSerializer(serializers.ModelSerializer):
    """Serializer for sidebar widgets with HTML content support."""
    
    class Meta:
        model = SidebarWidget
        fields = [
            'id', 'title', 'content', 'position', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HomepageSectionSerializer(serializers.ModelSerializer):
    """Serializer for homepage sections with nested article data."""
    
    image_url = serializers.SerializerMethodField()
    section_type_display = serializers.SerializerMethodField()
    section_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = HomepageSection
        fields = [
            'id', 'section_type', 'section_type_display', 'title', 'subtitle',
            'image', 'image_url', 'articles', 'section_articles', 'position', 'is_active',
            'max_articles', 'created_at'
        ]
        read_only_fields = [
            'id', 'section_type_display', 'image_url', 'section_articles', 'created_at'
        ]
    
    def get_image_url(self, obj):
        """Return absolute URL for section background image."""
        if obj.image:
            return obj.image.url
        return None
    
    def get_section_type_display(self, obj):
        """Return human-readable section type name."""
        return obj.get_section_type_display()
    
    def get_section_articles(self, obj):
        """Return nested serialized published articles for this section."""
        articles = obj.get_articles()
        return ArticleListSerializer(articles, many=True).data


class SEOSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SEO settings and meta tag defaults."""
    
    og_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SEOSettings
        fields = [
            'id', 'default_title', 'default_description', 'keywords',
            'og_image', 'og_image_url', 'google_analytics_id',
            'google_site_verification', 'updated_at'
        ]
        read_only_fields = ['id', 'og_image_url', 'updated_at']
    
    def get_og_image_url(self, obj):
        """Return absolute URL for Open Graph image."""
        if obj.og_image:
            return obj.og_image.url
        return None


__all__ = [
    'SiteSettingsSerializer',
    'SocialLinkSerializer',
    'AdvertisementBannerSerializer',
    'FooterSettingsSerializer',
    'SidebarWidgetSerializer',
    'HomepageSectionSerializer',
    'SEOSettingsSerializer',
]
