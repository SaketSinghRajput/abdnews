"""
Custom middleware for NewsHub application.

This module contains middleware classes for view counting, security headers,
and request logging across the NewsHub application.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.db import transaction

logger = logging.getLogger(__name__)


class ArticleViewCounterMiddleware(MiddlewareMixin):
    """
    Middleware to automatically increment article and video view counts.
    
    This middleware intercepts requests to article detail and video detail views
    and automatically increments the view count without requiring explicit
    service calls in the view.
    
    Uses caching to prevent duplicate counts from the same IP within an hour.
    Applies IP-based throttling and excludes author self-views.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view and increment article views if applicable.
        
        Args:
            request: The HTTP request object
            view_func: The view function being called
            view_args: Positional arguments for the view
            view_kwargs: Keyword arguments for the view
        
        Returns:
            None (continues with normal request processing)
        """
        # Check if this is an article detail view by examining the URL pattern
        try:
            resolved = resolve(request.path_info)
            
            # Check if this is the article detail endpoint
            # URL pattern: /api/articles/<slug>/
            if (resolved.url_name == 'article-detail' and 
                resolved.namespace == 'news' and 
                'slug' in view_kwargs):
                
                # Only increment for GET requests (not POST, PUT, DELETE)
                if request.method == 'GET':
                    self._increment_article_view(view_kwargs['slug'], request)

            # Check if this is the video detail endpoint
            # URL pattern: /api/videos/<slug>/
            if (resolved.url_name == 'video-detail' and 
                resolved.namespace == 'news' and 
                'slug' in view_kwargs and 
                request.method == 'GET'):
                self._increment_video_view(view_kwargs['slug'], request)
        except:
            # If URL resolution fails, just continue
            pass
        
        return None
    
    def _increment_article_view(self, slug: str, request):
        """
        Increment the view count for an article.
        
        Args:
            slug: The article slug
            request: The HTTP request object
        """
        try:
            # Import here to avoid circular imports
            from apps.news.models import Article
            
            # Use select_for_update to prevent race conditions
            with transaction.atomic():
                article = Article.objects.select_for_update().filter(
                    slug=slug,
                    status='published'
                ).first()
                
                if article:
                    # Check if this view should be counted
                    # Skip counting for:
                    # 1. The article author themselves
                    # 2. Staff/admin users (optional - remove if you want to count them)
                    # 3. Repeated views from the same IP within a short time
                    
                    should_count = True
                    
                    # Don't count views from the author
                    if request.user.is_authenticated and article.author:
                        if hasattr(article.author, 'user') and article.author.user == request.user:
                            should_count = False
                    
                    # Optional: Implement IP-based throttling using cache
                    # This prevents inflating view counts from repeated page refreshes
                    if should_count:
                        from django.core.cache import cache
                        ip_address = self._get_client_ip(request)
                        cache_key = f"article_view_{article.id}_{ip_address}"
                        
                        # Check if this IP has viewed this article recently (within 1 hour)
                        if cache.get(cache_key):
                            should_count = False
                        else:
                            # Set cache for 1 hour (3600 seconds)
                            cache.set(cache_key, True, 3600)
                    
                    if should_count:
                        article.views_count += 1
                        article.save(update_fields=['views_count'])
        except Exception as e:
            # Log the error but don't break the request
            logger.exception("Error incrementing article view: %s", e)
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        
        Args:
            request: The HTTP request object
        
        Returns:
            The client's IP address as a string
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _increment_video_view(self, slug: str, request):
        """
        Increment the view count for a video.
        
        Args:
            slug: The video slug
            request: The HTTP request object
        """
        try:
            # Import here to avoid circular imports
            from apps.news.models import Video
            from django.core.cache import cache

            # Use select_for_update to prevent race conditions
            with transaction.atomic():
                video = Video.objects.select_for_update().filter(
                    slug=slug,
                    is_active=True
                ).first()
                
                if video:
                    should_count = True

                    # Don't count views from the author
                    if request.user.is_authenticated and video.author:
                        if hasattr(video.author, 'user') and video.author.user == request.user:
                            should_count = False

                    if should_count:
                        ip_address = self._get_client_ip(request)
                        cache_key = f"video_view_{video.id}_{ip_address}"

                        if cache.get(cache_key):
                            should_count = False
                        else:
                            cache.set(cache_key, True, 3600)

                    if should_count:
                        video.views_count += 1
                        video.save(update_fields=['views_count'])
        except Exception as e:
            logger.exception("Error incrementing video view: %s", e)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        
        Args:
            request: The HTTP request object
            response: The HTTP response object
        
        Returns:
            The modified response object
        """
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests (useful for debugging and analytics).
    """
    
    def process_request(self, request):
        """
        Log incoming requests.
        
        Args:
            request: The HTTP request object
        
        Returns:
            None (continues with normal request processing)
        """
        # Only log API requests
        if request.path.startswith('/api/'):
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
                'ip': self._get_client_ip(request),
            }
            
            # In production, use proper logging
            # logger.info(f"API Request: {log_data}")
            logger.info("API Request: %s", log_data)
        
        return None
    
    def _get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
