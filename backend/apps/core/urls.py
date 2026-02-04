"""
URL configuration for NewsHub CMS API endpoints.
"""

from django.urls import path
from .views import (
    SiteSettingsAPIView,
    SocialLinksListAPIView,
    AdBannersListAPIView,
    FooterSettingsAPIView,
    SidebarWidgetsListAPIView,
    HomepageSectionsListAPIView,
    SEOSettingsAPIView,
)

app_name = 'core'

urlpatterns = [
    path('site-settings/', SiteSettingsAPIView.as_view(), name='site-settings'),
    path('social-links/', SocialLinksListAPIView.as_view(), name='social-links'),
    path('ads/', AdBannersListAPIView.as_view(), name='ads'),
    path('footer/', FooterSettingsAPIView.as_view(), name='footer'),
    path('sidebar/', SidebarWidgetsListAPIView.as_view(), name='sidebar'),
    path('homepage/', HomepageSectionsListAPIView.as_view(), name='homepage'),
    path('seo/', SEOSettingsAPIView.as_view(), name='seo'),
]
