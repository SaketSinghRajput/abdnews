# NewsHub API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Table of Contents
- [Authentication](#authentication)
- [Pagination](#pagination)
- [View Counter Throttling](#view-counter-throttling)
- [Media Files](#media-files)
- [CORS](#cors)
- [Filters & Ordering](#filters--ordering)
- [Articles](#articles)
- [Categories](#categories)
- [Tags](#tags)
- [Breaking News](#breaking-news)
- [Search](#search)
- [Comments](#comments)
- [Newsletter](#newsletter)
- [Videos](#videos)
- [Users & Authors](#users--authors)
- [Error Format](#error-format)

## Authentication
- **Token Auth**: `Authorization: Token <token>`
- **Session Auth**: Django session cookies

## Pagination
Default page size: **10**. Maximum: **100**

Query params:
- `page` (int)
- `page_size` (int)

Example response:
```json
{
  "count": 120,
  "next": "http://127.0.0.1:8000/api/articles/?page=2",
  "previous": null,
  "results": []
}
```

## View Counter Throttling
- Article and video detail views are counted once per IP per hour.
- Cache keys:
  - Articles: `article_view_<id>_<ip>`
  - Videos: `video_view_<id>_<ip>`

## Media Files
- `MEDIA_URL`: `/media/`
- Development serving via Django static helpers.
- Frontend `featured_image` and `thumbnail` fields can be absolute or relative.

## CORS
- Requests from the frontend origin are allowed in development.
- Preflight `OPTIONS` requests are supported for POST endpoints.

## Filters & Ordering
**Articles** support filtering by:
- `category` (slug)
- `tag` (slug)
- `is_featured` (true/false)
- `is_breaking` (true/false)
- `author` (author ID)

**Ordering**:
- `ordering=published_at` or `ordering=-published_at`
- `ordering=views_count` or `ordering=-views_count`

**Videos** support filtering by:
- `category` (slug)
- `is_featured` (true/false)
- `is_active` (true/false)

**Ordering**:
- `ordering=published_at` or `ordering=-published_at`
- `ordering=views_count` or `ordering=-views_count`

---

# Endpoints

## Articles

### List Articles
```
GET /api/articles/
```
**Query params:** `category`, `tag`, `is_featured`, `is_breaking`, `author`, `ordering`, `page`, `page_size`

**Response (sample):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Breaking: Major News Event",
      "slug": "breaking-major-news-event",
      "summary": "Brief summary...",
      "featured_image": "/media/articles/2024/01/image.jpg",
      "category_name": "Politics",
      "category_slug": "politics",
      "author_name": "John Doe",
      "author_designation": "Chief Political Analyst",
      "tags": [{"id": 1, "name": "Election", "slug": "election", "article_count": 15}],
      "read_time": 5,
      "comment_count": 12,
      "views_count": 1523,
      "is_featured": true,
      "is_breaking": false,
      "published_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Article Detail
```
GET /api/articles/<slug>/
```
**Behavior:** View count auto-increments.

**Response (sample):**
```json
{
  "id": 1,
  "title": "Breaking: Major News Event",
  "slug": "breaking-major-news-event",
  "summary": "Brief summary...",
  "content": "<p>Full rich text content...</p>",
  "featured_image": "/media/articles/2024/01/image.jpg",
  "category": {"id": 1, "name": "Politics", "slug": "politics", "article_count": 45},
  "category_name": "Politics",
  "tags": [{"id": 1, "name": "Election", "slug": "election", "article_count": 15}],
  "author": {
    "id": 1,
    "full_name": "John Doe",
    "designation": "Chief Political Analyst",
    "bio": "Award-winning journalist...",
    "profile_image": "/media/authors/john.jpg",
    "social_links": {"twitter": "https://twitter.com/johndoe"}
  },
  "author_name": "John Doe",
  "author_designation": "Chief Political Analyst",
  "comments": [
    {"id": 1, "user_name": "Jane Smith", "content": "Great article!", "created_at": "2024-01-15T11:00:00Z"}
  ],
  "comment_count": 12,
  "read_time": 5,
  "related_articles": [
    {"id": 2, "title": "Related Article", "slug": "related-article"}
  ],
  "views_count": 1523,
  "published_at": "2024-01-15T10:30:00Z"
}
```

### Trending Articles
```
GET /api/articles/trending/?days=7&limit=10
```

### Featured Articles
```
GET /api/articles/featured/?limit=5
```

### Most Commented Articles
```
GET /api/articles/most-commented/?limit=10
```

---

## Categories

### List Categories
```
GET /api/categories/
```

### Category Detail
```
GET /api/categories/<slug>/
```

---

## Tags

### List Tags
```
GET /api/tags/
```

---

## Breaking News

### List Breaking News
```
GET /api/breaking-news/
```

---

## Search

### Search Articles
```
GET /api/search/?q=ai&category=technology&tag=innovation
```

---

## Comments

### List Comments
```
GET /api/comments/?article=1
```

### Create Comment (Authenticated)
```
POST /api/comments/
```
**Body:**
```json
{
  "article": 1,
  "content": "Great article!"
}
```

---

## Newsletter

### Subscribe
```
POST /api/newsletter/subscribe/
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

### Unsubscribe
```
POST /api/newsletter/unsubscribe/
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

---

## Videos

### List Videos
```
GET /api/videos/?page_size=20&is_active=true
```
**Query params:** `category`, `is_featured`, `is_active`, `ordering`, `page`, `page_size`

**Response (sample):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "AI Revolution: The Future of Technology",
      "slug": "ai-revolution-the-future-of-technology",
      "description": "In-depth look at the latest AI advances...",
      "thumbnail": "/media/videos/thumbs/ai.jpg",
      "featured_image": "/media/videos/thumbs/ai.jpg",
      "video_url": "https://www.youtube.com/watch?v=example",
      "category_name": "Technology",
      "category_slug": "technology",
      "author_name": "NewsHub",
      "author_designation": "Video Team",
      "duration": "12:45",
      "views_count": 1203,
      "is_featured": true,
      "published_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Featured Videos
```
GET /api/videos/featured/?limit=6
```

### Video Detail
```
GET /api/videos/<slug>/
```

---

## Users & Authors

### List Users (Admin)
```
GET /api/users/users/
```

### Current User Profile
```
GET /api/users/users/me/
```

### List Authors
```
GET /api/users/authors/?is_featured=true
```

### Author Detail
```
GET /api/users/authors/<id>/
```

### Featured Authors
```
GET /api/users/authors/featured/
```

---

## Authentication

### Login (Token)
```
POST /api/users/auth/login/
```
**Body:**
```json
{
  "username": "username",
  "password": "password"
}
```

**Response:**
```json
{
  "token": "your-auth-token",
  "user_id": 1,
  "username": "username",
  "email": "user@example.com",
  "role": "journalist"
}
```

### Logout
```
POST /api/users/auth/logout/
```
**Auth:** Required

---

## Error Format
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```
