"""
API views for NewsHub CMS content management.

This module provides REST API endpoints for site-wide CMS models including
site settings, social links, advertisements, footer, sidebar, homepage sections, and SEO.
"""

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import (
    SiteSettings, SocialLink, AdvertisementBanner,
    FooterSettings, SidebarWidget, HomepageSection, SEOSettings
)
from .serializers import (
    SiteSettingsSerializer, SocialLinkSerializer, AdvertisementBannerSerializer,
    FooterSettingsSerializer, SidebarWidgetSerializer, HomepageSectionSerializer,
    SEOSettingsSerializer
)


class SiteSettingsAPIView(generics.RetrieveAPIView):
    """
    Retrieve global site settings and branding configuration.
    
    Returns singleton instance containing site name, logo, favicon,
    description, contact email, and primary brand color.
    """
    serializer_class = SiteSettingsSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        """Return the singleton SiteSettings instance."""
        return SiteSettings.load()


class SocialLinksListAPIView(generics.ListAPIView):
    """
    List all active social media links in display order.
    
    Returns social links filtered by is_active=True, ordered by
    position (order field) and platform name.
    """
    serializer_class = SocialLinkSerializer
    permission_classes = [AllowAny]
    queryset = SocialLink.objects.filter(is_active=True).order_by('order', 'platform')


class AdBannersListAPIView(generics.ListAPIView):
    """
    List active advertisement banners with optional position filtering.
    
    Query Parameters:
        position (str): Filter by banner position. Valid values:
            - header: Header banners
            - sidebar: Sidebar banners
            - footer: Footer banners
            - homepage: Homepage banners
            - article_top: Article top banners
            - article_bottom: Article bottom banners
    
    Returns banners filtered by is_active=True, ordered by position,
    order field, and creation date.
    """
    serializer_class = AdvertisementBannerSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter banners by position query parameter if provided."""
        queryset = AdvertisementBanner.objects.filter(is_active=True).order_by('position', 'order', '-created_at')
        
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        
        return queryset
    
    def get_serializer_context(self):
        """Add request to serializer context for absolute URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FooterSettingsAPIView(generics.RetrieveAPIView):
    """
    Retrieve footer settings and content.
    
    Returns singleton instance containing copyright text, social links toggle,
    extra footer links, and about text.
    """
    serializer_class = FooterSettingsSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        """Return the singleton FooterSettings instance."""
        return FooterSettings.load()


class SidebarWidgetsListAPIView(generics.ListAPIView):
    """
    List all active sidebar widgets in display order.
    
    Returns sidebar content blocks filtered by is_active=True,
    ordered by position field and creation date.
    """
    serializer_class = SidebarWidgetSerializer
    permission_classes = [AllowAny]
    queryset = SidebarWidget.objects.filter(is_active=True).order_by('position', '-created_at')


class HomepageSectionsListAPIView(generics.ListAPIView):
    """
    List active homepage sections with nested article data.
    
    Query Parameters:
        section_type (str): Filter by section type. Valid values:
            - hero: Hero section
            - featured: Featured articles section
            - trending: Trending news section
            - editorial: Editorial picks section
            - category: Category showcase section
            - video: Video section
    
    Returns sections filtered by is_active=True, ordered by position.
    Each section includes nested published articles limited by max_articles.
    """
    serializer_class = HomepageSectionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filter sections by section_type query parameter if provided."""
        queryset = HomepageSection.objects.filter(is_active=True).order_by('position', '-created_at')
        
        section_type = self.request.query_params.get('section_type')
        if section_type:
            queryset = queryset.filter(section_type=section_type)
        
        return queryset


class SEOSettingsAPIView(generics.RetrieveAPIView):
    """
    Retrieve SEO settings and default meta tags.
    
    Returns singleton instance containing default title, description,
    keywords, Open Graph image, and analytics tracking IDs.
    """
    serializer_class = SEOSettingsSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        """Return the singleton SEOSettings instance."""
        return SEOSettings.load()
