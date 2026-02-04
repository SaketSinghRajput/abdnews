# NewsHub API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Article Endpoints

### List Articles
```
GET /api/articles/
```
**Query Parameters:**
- `category` - Filter by category slug
- `tag` - Filter by tag slug  
- `is_featured` - Filter featured articles (true/false)
- `is_breaking` - Filter breaking news (true/false)
- `author` - Filter by author ID
- `ordering` - Sort by field (published_at, views_count, -published_at, -views_count)
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 10, max: 100)

**Response:** Paginated list of articles with basic info

### Article Detail
```
GET /api/articles/<slug>/
```
**Response:** Full article with content, comments, and related articles
**Note:** Automatically increments view count

### Trending Articles
```
GET /api/articles/trending/
```
**Query Parameters:**
- `days` - Number of days to consider (default: 7)
- `limit` - Maximum results (default: 10, max: 50)

**Response:** List of trending articles based on views

### Featured Articles
```
GET /api/articles/featured/
```
**Query Parameters:**
- `limit` - Maximum results (default: 5, max: 20)

**Response:** List of featured articles

### Most Commented Articles
```
GET /api/articles/most-commented/
```
**Query Parameters:**
- `limit` - Maximum results (default: 10, max: 50)

**Response:** Articles sorted by approved comment count

## Category Endpoints

### List Categories
```
GET /api/categories/
```
**Response:** All categories with article counts

### Category Detail
```
GET /api/categories/<slug>/
```
**Response:** Single category details

## Tag Endpoints

### List Tags
```
GET /api/tags/
```
**Response:** All tags with article counts

## Breaking News Endpoints

### List Breaking News
```
GET /api/breaking-news/
```
**Response:** Active breaking news items ordered by urgency

## Search Endpoint

### Search Articles
```
GET /api/search/
```
**Query Parameters:**
- `q` - Search query (required) - searches title, summary, and content
- `category` - Filter by category slug
- `tag` - Filter by tag slug
- `page` - Page number
- `page_size` - Results per page

**Response:** Paginated search results

## Comment Endpoints

### List/Create Comments
```
GET /api/comments/
POST /api/comments/
```
**GET Query Parameters:**
- `article` - Filter by article ID

**POST Body:**
```json
{
    "article": 1,
    "content": "Comment text here"
}
```
**Authentication:** Required for POST
**Response:** List of approved comments or newly created comment

## Newsletter Endpoints

### Subscribe to Newsletter
```
POST /api/newsletter/subscribe/
```
**Body:**
```json
{
    "email": "user@example.com"
}
```
**Response:** Success message with subscription status

### Unsubscribe from Newsletter
```
POST /api/newsletter/unsubscribe/
```
**Body:**
```json
{
    "email": "user@example.com"
}
```
**Response:** Success or error message

## User Endpoints

### List Users (Admin Only)
```
GET /api/users/users/
```
**Authentication:** Admin required

### Current User Profile
```
GET /api/users/users/me/
```
**Authentication:** Required

### List Authors
```
GET /api/users/authors/
```
**Query Parameters:**
- `is_featured` - Filter featured authors (true/false)

### Author Detail
```
GET /api/users/authors/<id>/
```

### Featured Authors
```
GET /api/users/authors/featured/
```

### Authentication

#### Login (Token)
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

#### Logout
```
POST /api/users/auth/logout/
```
**Authentication:** Required

## Response Format

### Success Response
```json
{
    "count": 100,
    "next": "http://127.0.0.1:8000/api/articles/?page=2",
    "previous": null,
    "results": [...]
}
```

### Error Response
```json
{
    "error": "Error message",
    "detail": "Detailed error information"
}
```

## Authentication

All authenticated endpoints require either:
1. **Token Authentication:** Add header `Authorization: Token <your-token>`
2. **Session Authentication:** Use Django session cookies

## Permissions

- **Public:** Most GET endpoints (articles, categories, tags, breaking news)
- **Authenticated:** Comment creation, user profile
- **Admin:** User management, unpublished content

## Example Usage

### Get All Articles
```bash
curl http://127.0.0.1:8000/api/articles/
```

### Get Technology Articles
```bash
curl http://127.0.0.1:8000/api/articles/?category=technology
```

### Search for Articles
```bash
curl "http://127.0.0.1:8000/api/search/?q=election&category=politics"
```

### Get Article Detail
```bash
curl http://127.0.0.1:8000/api/articles/breaking-news-headline/
```

### Create Comment (Authenticated)
```bash
curl -X POST http://127.0.0.1:8000/api/comments/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"article": 1, "content": "Great article!"}'
```

### Subscribe to Newsletter
```bash
curl -X POST http://127.0.0.1:8000/api/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```
