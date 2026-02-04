# Core App - Production-Ready Features Documentation

## Overview
The `apps.core` module provides essential production-ready utilities, middleware, validators, signals, and management commands for the NewsHub backend.

---

## 📁 File Structure

```
backend/apps/core/
├── apps.py                 # App configuration with signal registration
├── utils.py               # Utility functions for common operations
├── validators.py          # Custom validators for data validation
├── middleware.py          # Custom middleware components
├── signals.py            # Django signals for auto-operations
└── management/
    └── commands/
        └── populate_sample_data.py  # Sample data generation command
```

---

## 🛠️ Utils.py - Utility Functions

### Slug Generation
```python
from apps.core.utils import generate_unique_slug

# Auto-generate unique slugs
slug = generate_unique_slug(article_instance, "My Article Title")
# Returns: "my-article-title" or "my-article-title-2" if duplicate
```

### Image Upload Paths
```python
from apps.core.utils import article_image_upload_path, author_image_upload_path, category_icon_upload_path

# Usage in models:
class Article(models.Model):
    featured_image = models.ImageField(upload_to=article_image_upload_path)
    
# Generates path: articles/2026/02/abc123def456.jpg
```

### Search Helpers
```python
from apps.core.utils import build_search_query, get_search_results

# Build complex search queries
query = build_search_query("artificial intelligence", ['title', 'summary', 'content'])

# Apply search to queryset
results = get_search_results(Article.objects.all(), "AI machine learning", ['title', 'content'])
```

### Text Utilities
```python
from apps.core.utils import format_reading_time, truncate_text

reading_time = format_reading_time(1500)  # "8 min read"
excerpt = truncate_text("Long article...", max_length=160)  # Truncated with "..."
```

---

## ✅ Validators.py - Data Validation

### Image Validators
```python
from apps.core.validators import validate_article_image, validate_author_image, validate_category_icon

# Article images: min 800x450px, max 5MB
validate_article_image(uploaded_file)

# Author images: min 200x200px, max 2MB
validate_author_image(uploaded_file)

# Category icons: min 100x100px, max 1MB
validate_category_icon(uploaded_file)
```

### Content Validators
```python
from apps.core.validators import validate_content_length, validate_title_length, validate_slug

# Validate article content (100-50000 chars)
validate_content_length(article_content)

# Validate title (10-200 chars)
validate_title_length(article_title)

# Validate slug format
validate_slug("my-article-slug")
```

### Using in Models
```python
from django.db import models
from apps.core.validators import validate_article_image, validate_title_length

class Article(models.Model):
    title = models.CharField(max_length=200, validators=[validate_title_length])
    featured_image = models.ImageField(
        upload_to='articles/',
        validators=[validate_article_image]
    )
```

---

## 🔄 Middleware.py - Custom Middleware

### ArticleViewCounterMiddleware
**Purpose:** Automatically increment article and video view counts on GET requests

**Features:**
- Intercepts article detail view requests
- Increments `views_count` field automatically
- Prevents author self-views from counting
- IP-based throttling (1 hour cooldown per IP)
- Race-condition safe with `select_for_update()`

**Configuration:**
```python
# backend/config/settings.py
MIDDLEWARE = [
    # ... other middleware
    'apps.core.middleware.ArticleViewCounterMiddleware',
]
```

**How It Works:**
1. Detects requests to `/api/articles/<slug>/` and `/api/videos/<slug>/`
2. Checks if user is the content author (skip if yes)
3. Uses cache to prevent duplicate counts within 1 hour
4. Atomically increments `views_count` field

**Cache Requirement:**
Requires Django cache backend. Default settings use local-memory cache:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

For production, use Redis:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

**Cache Keys:**
- Articles: `article_view_<id>_<ip>`
- Videos: `video_view_<id>_<ip>`

### SecurityHeadersMiddleware
Adds security headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### RequestLoggingMiddleware
Logs all API requests (useful for debugging and analytics)

---

## 🔔 Signals.py - Auto-Operations

### Auto Slug Generation
**Signals:** `pre_save` on Article and Category models

**Behavior:**
- If `slug` field is empty, auto-generates from `title` (Article) or `name` (Category)
- Ensures uniqueness by appending counter if needed
- Example: "My Article" → "my-article" or "my-article-2"

```python
# No need to manually set slug
article = Article(title="Breaking News: AI Breakthrough")
article.save()
# article.slug is now "breaking-news-ai-breakthrough"
```

### Category Article Count Auto-Update
**Signals:** `post_save`, `post_delete` on Article model

**Behavior:**
- Automatically updates `Category.article_count` field
- Triggers when:
  - Article is created
  - Article is updated (category changed)
  - Article is deleted
- Only counts **published** articles

```python
# Manually trigger update (usually not needed)
from apps.core.signals import update_category_count
update_category_count(category_instance)
```

### Registering Signals
Signals are auto-registered via `apps.core.apps.CoreConfig.ready()`:
```python
# backend/apps/core/apps.py
class CoreConfig(AppConfig):
    def ready(self):
        import apps.core.signals  # noqa
```

---

## 🎯 Management Commands

### populate_sample_data
**Purpose:** Generate sample data for testing and development

**Usage:**
```bash
# Create 20 articles with sample data
python manage.py populate_sample_data

# Clear existing data and create 50 articles
python manage.py populate_sample_data --flush --articles 50

# Get help
python manage.py populate_sample_data --help
```

**What It Creates:**

1. **Users (12 total):**
   - 1 admin: `admin@newshub.com` / `admin123`
   - 2 editors: `editor@newshub.com` / `password123`
   - 5 journalists with author profiles
   - 5 regular users (for comments)

2. **Authors (5 total):**
   - John Doe (Senior Journalist)
   - Sarah Wilson (Political Correspondent)
   - David Brown (Sports Reporter)
   - Emily Davis (Entertainment Writer)
   - Michael Taylor (Science Correspondent)

3. **Categories (10):**
   - Technology, Business, Politics, Sports, Entertainment
   - Science, Health, World, Lifestyle, Opinion

4. **Tags (20):**
   - Breaking News, Trending, Featured, Analysis, etc.

5. **Articles (configurable, default 20):**
   - Randomly assigned to authors and categories
   - 2-5 tags per article
   - 30% marked as featured
   - Random view counts (100-5000)
   - Published dates within last 30 days

6. **Comments:**
   - 2-5 comments on 15 random articles
   - 80% approval rate

7. **Breaking News (3):**
   - Latest 3 articles marked as breaking

8. **Newsletter Subscribers (6):**
   - 5 active, 1 inactive

**Sample Credentials:**
```
Admin:      admin@newshub.com / admin123
Editor:     editor@newshub.com / password123
Journalist: john.doe@newshub.com / password123
```

---

## ⚙️ Settings Configuration

### Media File Handling
```python
# backend/config/settings.py

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
```

### URL Configuration
```python
# backend/config/urls.py

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Production:** Use Nginx/Apache to serve media files:
```nginx
location /media/ {
    alias /path/to/newshub/backend/media/;
}
```

---

## ✅ Production Deployment Checklist

1. **Cache Backend**: Configure Redis cache for view throttling.
2. **Media Storage**: Serve media with Nginx/Apache or cloud storage (S3/GCS).
3. **Security**: Set `DEBUG=False`, configure `ALLOWED_HOSTS`, rotate `SECRET_KEY`.
4. **HTTPS**: Enable HTTPS and secure cookies.
5. **Database**: Use PostgreSQL/MySQL for production.
6. **Monitoring**: Add error tracking (Sentry) and request logging.
7. **Backups**: Schedule database and media backups.

---

## 🧯 Troubleshooting

### View counts not incrementing
- Ensure `apps.core.middleware.ArticleViewCounterMiddleware` is in `MIDDLEWARE`.
- Confirm cache backend is configured and available.
- Verify you are hitting `/api/articles/<slug>/` or `/api/videos/<slug>/` with GET.

### Repeated views still increasing
- Check cache backend is persistent (LocMem resets on server restart).
- Ensure cache keys are not being evicted due to low cache memory.

### Media files returning 404
- Confirm `MEDIA_URL` and `MEDIA_ROOT` are set in settings.
- Verify `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` is in URLs for development.
- Ensure files exist in the expected `media/` path.

---

## 🚀 Usage Examples

### Example 1: Creating an Article with Auto-Slug
```python
from apps.news.models import Article, Category
from apps.users.models import Author

author = Author.objects.first()
category = Category.objects.get(slug='technology')

article = Article.objects.create(
    title="Artificial Intelligence Breakthrough in 2026",  # No slug needed!
    summary="Researchers achieve new milestone in AI development",
    content="<p>Full article content...</p>",
    author=author,
    category=category,
    status='published'
)

# article.slug is now "artificial-intelligence-breakthrough-in-2026"
# category.article_count is automatically updated
```

### Example 2: Using Validators in Forms
```python
from django import forms
from apps.core.validators import validate_article_image, validate_title_length

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'featured_image', 'content']
        
    def clean_title(self):
        title = self.cleaned_data['title']
        validate_title_length(title)  # Raises ValidationError if invalid
        return title
    
    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        if image:
            validate_article_image(image)
        return image
```

### Example 3: Manual Search Query
```python
from apps.core.utils import build_search_query, get_search_results
from apps.news.models import Article

# Search for articles
search_term = "climate change renewable energy"
results = get_search_results(
    Article.objects.filter(status='published'),
    search_term,
    ['title', 'summary', 'content']
)

# Or build query manually
query = build_search_query(search_term, ['title', 'content'])
articles = Article.objects.filter(query)
```

### Example 4: Generating Sample Data for Testing
```python
# In your test file
from django.core.management import call_command
from django.test import TestCase

class ArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Populate sample data before running tests
        call_command('populate_sample_data', '--articles', '10', verbosity=0)
    
    def test_article_views_increment(self):
        # Test with pre-populated data
        article = Article.objects.first()
        initial_views = article.views_count
        
        # Make GET request
        response = self.client.get(f'/api/articles/{article.slug}/')
        
        # Check view count incremented
        article.refresh_from_db()
        self.assertEqual(article.views_count, initial_views + 1)
```

---

## 🔧 Customization

### Custom Upload Paths
```python
# backend/apps/core/utils.py

def custom_upload_path(instance, filename: str) -> str:
    """Custom upload path for your specific needs."""
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('custom_folder', instance.category.slug, unique_filename)
```

### Custom Validators
```python
# backend/apps/core/validators.py

def validate_video_file(file):
    """Validate uploaded video files."""
    allowed_types = ['video/mp4', 'video/webm']
    if file.content_type not in allowed_types:
        raise ValidationError("Only MP4 and WebM videos allowed")
    
    if file.size > 100 * 1024 * 1024:  # 100 MB
        raise ValidationError("Video file too large (max 100MB)")
```

### Custom Signals
```python
# backend/apps/core/signals.py

@receiver(post_save, sender=Article)
def notify_subscribers_on_new_article(sender, instance, created, **kwargs):
    """Send email to subscribers when new article is published."""
    if created and instance.status == 'published':
        # Send notifications
        from apps.news.services import NewsletterService
        NewsletterService.send_new_article_notification(instance)
```

---

## 📊 Performance Considerations

### View Counter Middleware
- Uses Django cache to prevent duplicate counts
- Atomic database operations prevent race conditions
- Consider using Redis cache in production for distributed systems

### Slug Generation
- Runs only when slug is empty (pre_save signal)
- Database query executed to check uniqueness
- For high-traffic sites, consider pre-generating slugs in admin

### Category Count Updates
- Triggered on every article save/delete
- Uses `update()` for efficient database operations
- No N+1 queries

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test apps.core

# Test specific component
python manage.py test apps.core.tests.test_utils
python manage.py test apps.core.tests.test_validators
python manage.py test apps.core.tests.test_middleware
python manage.py test apps.core.tests.test_signals
```

---

## 📝 Notes

- All validators raise `django.core.exceptions.ValidationError`
- Middleware is order-dependent; place custom middleware after Django's built-in ones
- Signals are registered automatically when app is loaded
- Management commands follow Django's command structure
- All utilities are reusable across the project

---

## 🎓 Best Practices

1. **Always use validators** for user-uploaded files
2. **Enable caching** for ArticleViewCounterMiddleware in production
3. **Monitor signal performance** in high-traffic scenarios
4. **Use populate_sample_data** for development/testing only
5. **Customize upload paths** based on your storage backend (S3, etc.)

---

## 🔗 Related Documentation

- [Django Signals Documentation](https://docs.djangoproject.com/en/4.2/topics/signals/)
- [Django Middleware Documentation](https://docs.djangoproject.com/en/4.2/topics/http/middleware/)
- [Django Management Commands](https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/)
- [Django File Uploads](https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/)

---

**Version:** 1.0  
**Last Updated:** February 4, 2026  
**Maintainer:** NewsHub Development Team
