"""
Business logic services for NewsHub.

This module contains service classes that encapsulate business logic
for articles, newsletter management, and other news-related operations.
"""

from django.db.models import Q, F, Count
from django.utils import timezone
from datetime import timedelta
from .models import Article, NewsletterSubscriber, BreakingNews
from apps.core.utils import get_search_results


class ArticleService:
    """
    Service class for article-related business logic.
    Handles view counting, trending calculations, search, and filtering.
    """
    
    @staticmethod
    def increment_views(article):
        """
        Atomically increment article view count.
        
        Args:
            article: Article instance
        """
        article.increment_views()
    
    @staticmethod
    def get_trending(days=7, limit=10):
        """
        Get trending articles based on views in recent days.
        
        Args:
            days: Number of days to consider (default: 7)
            limit: Maximum number of articles to return (default: 10)
        
        Returns:
            QuerySet of trending articles
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            published_at__gte=cutoff_date
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-views_count', '-published_at')[:limit]
    
    @staticmethod
    def get_featured(limit=5):
        """
        Get featured articles.
        
        Args:
            limit: Maximum number of articles to return (default: 5)
        
        Returns:
            QuerySet of featured articles
        """
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            is_featured=True
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')[:limit]
    
    @staticmethod
    def get_breaking():
        """
        Get breaking news articles.
        
        Returns:
            QuerySet of breaking news articles
        """
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            is_breaking=True
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')[:10]
    
    @staticmethod
    def search_articles(query, category=None, tags=None):
        """
        Search articles by title, summary, and content.
        
        Args:
            query: Search query string
            category: Optional category slug to filter by
            tags: Optional list of tag slugs to filter by
        
        Returns:
            QuerySet of matching articles
        """
        articles = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        )
        
        # Text search across title, summary, and content
        if query:
            articles = get_search_results(
                articles,
                query,
                ['title', 'summary', 'content']
            )
        
        # Filter by category
        if category:
            articles = articles.filter(category__slug=category)
        
        # Filter by tags
        if tags:
            articles = articles.filter(tags__slug__in=tags).distinct()
        
        return articles.annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')
    
    @staticmethod
    def get_by_category(category_slug, limit=None):
        """
        Get articles by category.
        
        Args:
            category_slug: Category slug
            limit: Optional limit on number of articles
        
        Returns:
            QuerySet of articles in the category
        """
        articles = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            category__slug=category_slug
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')
        
        if limit:
            articles = articles[:limit]
        
        return articles
    
    @staticmethod
    def get_by_tag(tag_slug, limit=None):
        """
        Get articles by tag.
        
        Args:
            tag_slug: Tag slug
            limit: Optional limit on number of articles
        
        Returns:
            QuerySet of articles with the tag
        """
        articles = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            tags__slug=tag_slug
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at').distinct()
        
        if limit:
            articles = articles[:limit]
        
        return articles
    
    @staticmethod
    def get_by_author(author_id, limit=None):
        """
        Get articles by author.
        
        Args:
            author_id: Author ID
            limit: Optional limit on number of articles
        
        Returns:
            QuerySet of articles by the author
        """
        articles = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            author_id=author_id
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')
        
        if limit:
            articles = articles[:limit]
        
        return articles
    
    @staticmethod
    def get_recent(limit=10):
        """
        Get most recent published articles.
        
        Args:
            limit: Maximum number of articles to return (default: 10)
        
        Returns:
            QuerySet of recent articles
        """
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-published_at')[:limit]
    
    @staticmethod
    def get_most_commented(limit=10):
        """
        Get articles with most approved comments.
        
        Args:
            limit: Maximum number of articles to return (default: 10)
        
        Returns:
            QuerySet of articles ordered by comment count
        """
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).annotate(
            approved_comment_count=Count('comments', filter=Q(comments__is_approved=True)),
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).filter(
            approved_comment_count__gt=0
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related(
            'tags'
        ).order_by('-approved_comment_count', '-published_at')[:limit]


class NewsletterService:
    """
    Service class for newsletter subscription management.
    """
    
    @staticmethod
    def subscribe(email):
        """
        Subscribe an email to the newsletter.
        
        Args:
            email: Email address to subscribe
        
        Returns:
            Tuple of (subscriber instance, created boolean)
        """
        # Check if email already exists
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if not subscriber.is_active:
                # Reactivate subscription
                subscriber.resubscribe()
                return subscriber, False
            return subscriber, False
        except NewsletterSubscriber.DoesNotExist:
            # Create new subscription
            subscriber = NewsletterSubscriber.objects.create(email=email)
            return subscriber, True
    
    @staticmethod
    def unsubscribe(email):
        """
        Unsubscribe an email from the newsletter.
        
        Args:
            email: Email address to unsubscribe
        
        Returns:
            Boolean indicating if unsubscribe was successful
        """
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if subscriber.is_active:
                subscriber.unsubscribe()
                return True
            return False  # Already unsubscribed
        except NewsletterSubscriber.DoesNotExist:
            return False  # Email not found
    
    @staticmethod
    def get_active_subscribers():
        """
        Get all active newsletter subscribers.
        
        Returns:
            QuerySet of active subscribers
        """
        return NewsletterSubscriber.objects.filter(is_active=True)
    
    @staticmethod
    def get_subscriber_count():
        """
        Get count of active subscribers.
        
        Returns:
            Integer count of active subscribers
        """
        return NewsletterSubscriber.objects.filter(is_active=True).count()


class BreakingNewsService:
    """
    Service class for breaking news management.
    """
    
    @staticmethod
    def get_active():
        """
        Get all active breaking news items.
        
        Returns:
            QuerySet of active breaking news ordered by urgency
        """
        return BreakingNews.get_active_breaking_news()
    
    @staticmethod
    def create_breaking_news(text, urgent=True):
        """
        Create a new breaking news item.
        
        Args:
            text: Breaking news text
            urgent: Whether the news is urgent (default: True)
        
        Returns:
            BreakingNews instance
        """
        return BreakingNews.objects.create(
            text=text,
            urgent=urgent,
            is_active=True
        )
    
    @staticmethod
    def deactivate_old_breaking_news(hours=24):
        """
        Deactivate breaking news items older than specified hours.
        
        Args:
            hours: Number of hours after which to deactivate (default: 24)
        
        Returns:
            Number of items deactivated
        """
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return BreakingNews.objects.filter(
            created_at__lt=cutoff_time,
            is_active=True
        ).update(is_active=False)
