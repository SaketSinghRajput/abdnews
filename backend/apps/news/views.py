"""
API views for NewsHub.

This module provides REST API endpoints for articles, categories,
breaking news, comments, newsletter subscriptions, and search functionality.
"""

from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .models import Article, Category, Tag, Comment, BreakingNews, NewsletterSubscriber, Video
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
    BreakingNewsSerializer,
    NewsletterSubscriberSerializer,
    VideoSerializer,
    VideoDetailSerializer,
)
from .services import ArticleService, NewsletterService, BreakingNewsService


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for API responses"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ArticleListView(generics.ListAPIView):
    """
    List articles with filtering, ordering, and pagination.
    
    Query parameters:
    - category: Filter by category slug
    - tag: Filter by tag slug
    - is_featured: Filter featured articles (true/false)
    - is_breaking: Filter breaking news (true/false)
    - ordering: Sort by field (published_at, views_count, -published_at, -views_count)
    - page: Page number
    - page_size: Results per page (max 100)
    """
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['published_at', 'views_count', 'created_at']
    ordering = ['-published_at']
    
    def get_queryset(self):
        """Get filtered queryset of published articles"""
        queryset = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related('tags')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by tag
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag).distinct()
        
        # Filter by featured status
        is_featured = self.request.query_params.get('is_featured')
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == 'true'
            queryset = queryset.filter(is_featured=is_featured_bool)
        
        # Filter by breaking status
        is_breaking = self.request.query_params.get('is_breaking')
        if is_breaking is not None:
            is_breaking_bool = is_breaking.lower() == 'true'
            queryset = queryset.filter(is_breaking=is_breaking_bool)
        
        # Filter by author
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)
        
        return queryset


class ArticleDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single article by slug.
    Returns limited preview for non-subscribed users.
    Full content only for subscribed users or admins.
    """
    
    serializer_class = ArticleDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get published articles with related data"""
        return Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED
        ).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related(
            'category', 'author', 'author__user'
        ).prefetch_related('tags', 'comments')
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve article with subscription check.
        Non-subscribed users get limited preview.
        """
        instance = self.get_object()
        
        # Check subscription status
        user = request.user
        has_access = False
        
        if user.is_authenticated:
            # Admin always has access
            if hasattr(user, 'role') and user.role == 'admin':
                has_access = True
            # Check subscription
            elif hasattr(user, 'has_active_subscription'):
                has_access = user.has_active_subscription
        
        # Serialize data
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # If no subscription, return limited preview
        if not has_access:
            # Limit content to first 200 characters
            if data.get('content'):
                data['content'] = data['content'][:200] + '...'
                data['is_preview'] = True
                data['message'] = 'Subscribe to read the full article'
                data['requires_subscription'] = True
        else:
            data['is_preview'] = False
            data['requires_subscription'] = False
        
        return Response(data)


class TrendingArticlesView(generics.ListAPIView):
    """
    Get trending articles based on views.
    
    Query parameters:
    - days: Number of days to consider (default: 7)
    - limit: Maximum results (default: 10, max: 50)
    """
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get trending articles"""
        days = int(self.request.query_params.get('days', 7))
        limit = min(int(self.request.query_params.get('limit', 10)), 50)
        
        return ArticleService.get_trending(days=days, limit=limit)


class FeaturedArticlesView(generics.ListAPIView):
    """
    Get featured articles.
    
    Query parameters:
    - limit: Maximum results (default: 5, max: 20)
    """
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get featured articles"""
        limit = min(int(self.request.query_params.get('limit', 5)), 20)
        return ArticleService.get_featured(limit=limit)


class CategoryListView(generics.ListAPIView):
    """
    List all categories with article counts.
    """
    
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.all().order_by('name')


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single category by slug.
    """
    
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    queryset = Category.objects.all()


class TagListView(generics.ListAPIView):
    """
    List all tags with article counts.
    """
    
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    queryset = Tag.objects.all().order_by('name')


class BreakingNewsListView(generics.ListAPIView):
    """
    List active breaking news items.
    """
    
    serializer_class = BreakingNewsSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get active breaking news"""
        return BreakingNewsService.get_active()


class SearchView(generics.ListAPIView):
    """
    Search articles by title, summary, and content.
    
    Query parameters:
    - q: Search query (required)
    - category: Filter by category slug
    - tag: Filter by tag slug
    - page: Page number
    - page_size: Results per page
    """
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Search articles"""
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category')
        tag = self.request.query_params.get('tag')
        
        if not query:
            return Article.objects.none()
        
        # Use service for search
        tags = [tag] if tag else None
        return ArticleService.search_articles(
            query=query,
            category=category,
            tags=tags
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """
    List and create comments.
    
    GET: List approved comments for an article (query param: article)
    POST: Create a new comment (requires authentication)
    """
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get approved comments, optionally filtered by article"""
        queryset = Comment.objects.filter(
            is_approved=True
        ).select_related('user', 'article')
        
        # Filter by article
        article_id = self.request.query_params.get('article')
        if article_id:
            queryset = queryset.filter(article_id=article_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create comment with current user"""
        serializer.save(user=self.request.user)


class NewsletterSubscribeView(APIView):
    """
    Subscribe to newsletter.
    
    POST: Subscribe an email to the newsletter
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Subscribe to newsletter"""
        serializer = NewsletterSubscriberSerializer(data=request.data)
        
        if serializer.is_valid():
            subscriber, created = NewsletterService.subscribe(
                serializer.validated_data['email']
            )
            
            if created:
                return Response(
                    {
                        'message': 'Successfully subscribed to newsletter',
                        'email': subscriber.email
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'message': 'Email already subscribed or reactivated',
                        'email': subscriber.email
                    },
                    status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsletterUnsubscribeView(APIView):
    """
    Unsubscribe from newsletter.
    
    POST: Unsubscribe an email from the newsletter
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Unsubscribe from newsletter"""
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = NewsletterService.unsubscribe(email)
        
        if success:
            return Response(
                {'message': 'Successfully unsubscribed from newsletter'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Email not found or already unsubscribed'},
                status=status.HTTP_404_NOT_FOUND
            )


class MostCommentedArticlesView(generics.ListAPIView):
    """
    Get articles with most comments.
    
    Query parameters:
    - limit: Maximum results (default: 10, max: 50)
    """
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get most commented articles"""
        limit = min(int(self.request.query_params.get('limit', 10)), 50)
        return ArticleService.get_most_commented(limit=limit)


class VideoListView(generics.ListAPIView):
    """
    List videos with filtering, ordering, and pagination.
    
    Query parameters:
    - category: Filter by category slug
    - is_featured: Filter featured videos (true/false)
    - ordering: Sort by field (published_at, views_count, -published_at, -views_count)
    - page: Page number
    - page_size: Results per page (max 100)
    """
    
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['published_at', 'views_count', '-published_at', '-views_count']
    ordering = ['-published_at']
    
    def get_queryset(self):
        """Get active videos"""
        queryset = Video.objects.filter(is_active=True).select_related('category', 'author')

        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset


class VideoDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single video by slug.
    
    URL parameter:
    - slug: Video slug
    """
    
    serializer_class = VideoDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active videos"""
        return Video.objects.filter(is_active=True).select_related('category', 'author')


class FeaturedVideosView(generics.ListAPIView):
    """
    Get featured videos for homepage.
    
    Query parameters:
    - limit: Maximum results (default: 6, max: 20)
    """
    
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get featured active videos"""
        limit = min(int(self.request.query_params.get('limit', 6)), 20)
        return Video.objects.filter(is_active=True, is_featured=True).select_related(
            'category', 'author'
        )[:limit]
