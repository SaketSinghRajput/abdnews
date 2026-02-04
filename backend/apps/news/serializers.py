"""
Serializers for NewsHub API endpoints.

This module provides DRF serializers for all news-related models,
with optimized field selection and nested relationships.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import Category, Tag, Article, Comment, BreakingNews, NewsletterSubscriber, Video
from apps.users.serializers import AuthorSerializer

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model with article count"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'article_count']
        read_only_fields = ['id', 'slug', 'article_count']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'article_count']
        read_only_fields = ['id', 'slug']
    
    def get_article_count(self, obj):
        """Get count of articles with this tag"""
        return obj.articles.filter(status=Article.ArticleStatus.PUBLISHED).count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model with user details"""
    
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'user', 'user_name', 'user_email',
            'content', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_approved']
    
    def get_user_name(self, obj):
        """Get user's full name or username"""
        return obj.user.get_full_name() or obj.user.username
    
    def get_user_email(self, obj):
        """Get user's email (only for approved comments)"""
        if obj.is_approved:
            return obj.user.email
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for article lists.
    Optimized for performance with minimal nested data.
    """
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    author_name = serializers.SerializerMethodField()
    author_designation = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    read_time = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'featured_image',
            'category_name', 'category_slug', 'author_name', 'author_designation',
            'tags', 'status', 'is_breaking', 'is_featured',
            'views_count', 'comment_count', 'read_time',
            'published_at', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'created_at']
    
    def get_author_name(self, obj):
        """Get author's full name"""
        return obj.author.get_full_name() if obj.author else 'Anonymous'
    
    def get_author_designation(self, obj):
        """Get author's designation"""
        return obj.author.designation if obj.author else ''
    
    def get_read_time(self, obj):
        """Get estimated reading time"""
        return obj.get_read_time()


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for article detail view.
    Includes full content, nested relationships, and related data.
    Matches frontend expectations with flat structure for author fields.
    """
    
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    author_designation = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    read_time = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)
    related_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'featured_image',
            'category', 'category_name', 'tags', 'author', 'author_name', 'author_designation',
            'status', 'is_breaking', 'is_featured',
            'views_count', 'comment_count', 'read_time', 'comments',
            'related_articles', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'views_count', 'comment_count',
            'created_at', 'updated_at'
        ]
    
    def get_author_name(self, obj):
        """Get author's full name"""
        return obj.author.get_full_name() if obj.author else 'Anonymous'
    
    def get_author_designation(self, obj):
        """Get author's designation"""
        return obj.author.designation if obj.author else ''
    
    def get_comments(self, obj):
        """Get approved comments for this article"""
        comments = obj.comments.filter(is_approved=True).select_related('user')
        return CommentSerializer(comments, many=True).data
    
    def get_read_time(self, obj):
        """Get estimated reading time"""
        return obj.get_read_time()
    
    def get_related_articles(self, obj):
        """Get related articles based on category and tags"""
        # Get articles from same category with shared tags
        related = Article.objects.filter(
            status=Article.ArticleStatus.PUBLISHED,
            category=obj.category
        ).exclude(id=obj.id).annotate(
            comment_count=Count('comments', filter=Q(comments__is_approved=True))
        ).select_related('category', 'author').prefetch_related('tags')
        
        # Prioritize articles with shared tags
        shared_tag_ids = obj.tags.values_list('id', flat=True)
        if shared_tag_ids:
            related = related.filter(tags__in=shared_tag_ids).distinct()
        
        # Limit to 4 related articles
        related = related[:4]
        
        return ArticleListSerializer(related, many=True).data


class BreakingNewsSerializer(serializers.ModelSerializer):
    """Serializer for breaking news items"""
    
    time_display = serializers.SerializerMethodField()
    
    class Meta:
        model = BreakingNews
        fields = [
            'id', 'text', 'urgent', 'is_active',
            'time_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_time_display(self, obj):
        """Get human-readable time display"""
        return obj.get_time_display()


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscriptions"""
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'is_active', 'subscribed_at']
        read_only_fields = ['id', 'is_active', 'subscribed_at']
    
    def validate_email(self, value):
        """Validate email is not already subscribed"""
        if self.instance is None:  # Only check on creation
            if NewsletterSubscriber.objects.filter(email=value, is_active=True).exists():
                raise serializers.ValidationError('This email is already subscribed to our newsletter.')
        return value
    
    def create(self, validated_data):
        """Create or reactivate newsletter subscription"""
        email = validated_data['email']
        
        # Check if email exists but is inactive
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if not subscriber.is_active:
                subscriber.resubscribe()
                return subscriber
            return subscriber
        except NewsletterSubscriber.DoesNotExist:
            # Create new subscriber
            return super().create(validated_data)


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model with author and category details"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    author_name = serializers.SerializerMethodField()
    author_designation = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'featured_image', 'video_url', 'category', 'category_name',
            'category_slug', 'author', 'author_name', 'author_designation',
            'duration', 'views_count', 'is_featured', 'is_active',
            'published_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'published_at', 'updated_at']
    
    def get_author_name(self, obj):
        """Get author's full name"""
        return obj.author.get_full_name() if obj.author else 'NewsHub'
    
    def get_author_designation(self, obj):
        """Get author's designation"""
        return obj.author.designation if obj.author else 'Video Team'
    
    def get_featured_image(self, obj):
        """Return thumbnail as featured_image"""
        if obj.thumbnail:
            return obj.thumbnail.url
        return None


class VideoDetailSerializer(VideoSerializer):
    """Extended serializer for detailed video view"""
    
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta(VideoSerializer.Meta):
        fields = VideoSerializer.Meta.fields
