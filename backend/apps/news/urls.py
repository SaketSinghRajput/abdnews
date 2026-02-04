"""
URL configuration for news API endpoints.
"""

from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    TrendingArticlesView,
    FeaturedArticlesView,
    CategoryListView,
    CategoryDetailView,
    TagListView,
    BreakingNewsListView,
    SearchView,
    CommentListCreateView,
    NewsletterSubscribeView,
    NewsletterUnsubscribeView,
    MostCommentedArticlesView,
    VideoListView,
    VideoDetailView,
    FeaturedVideosView,
)

app_name = 'news'

urlpatterns = [
    # Article endpoints - order matters! Specific patterns before generic
    path('articles/trending/', TrendingArticlesView.as_view(), name='article-trending'),
    path('articles/featured/', FeaturedArticlesView.as_view(), name='article-featured'),
    path('articles/most-commented/', MostCommentedArticlesView.as_view(), name='article-most-commented'),
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    
    # Category endpoints
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Tag endpoints
    path('tags/', TagListView.as_view(), name='tag-list'),
    
    # Breaking news endpoints
    path('breaking-news/', BreakingNewsListView.as_view(), name='breaking-news-list'),
    
    # Search endpoint
    path('search/', SearchView.as_view(), name='search'),
    
    # Comment endpoints
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    
    # Newsletter endpoints
    path('newsletter/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/subscribe/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    
    # Video endpoints
    path('videos/featured/', FeaturedVideosView.as_view(), name='video-featured'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<slug:slug>/', VideoDetailView.as_view(), name='video-detail'),
]
