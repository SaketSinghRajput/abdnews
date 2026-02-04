# NewsHub Backend

A production-ready Django backend for NewsHub, providing REST APIs for articles, categories, tags, authors, comments, breaking news, and newsletter subscriptions.

## Overview
- **Framework:** Django 4.2 + Django REST Framework
- **Auth:** Token + Session
- **Content:** CKEditor rich text for articles
- **Filtering/Search:** django-filter + search endpoints
- **Media:** Local media storage (development)

## Features
- Role-based user system (Admin, Editor, Journalist)
- Author profiles linked to users
- News content management (articles, categories, tags)
- Breaking news and newsletter subscriptions
- Public API endpoints with pagination, ordering, filters, and search
- Admin CMS with rich text and previews

## Architecture
- `apps/users/` — Custom user model and author profiles
- `apps/news/` — News content models and APIs
- `apps/core/` — Utilities, validators, middleware, signals, commands

## Model Relationships (ER Diagram)
```mermaid
erDiagram
    CustomUser ||--o| Author : "has profile"
    Author ||--o{ Article : "writes"
    Author ||--o{ Video : "creates"
    Category ||--o{ Article : "categorizes"
    Category ||--o{ Video : "categorizes"
    Tag }o--o{ Article : "tags"
    Article ||--o{ Comment : "has"
    CustomUser ||--o{ Comment : "writes"
    
    CustomUser {
        int id PK
        string username
        string email
        string role
        string phone_number
    }
    
    Author {
        int id PK
        int user_id FK
        string bio
        string designation
        image profile_image
        string social_links
        bool is_featured
        int article_count
    }
    
    Category {
        int id PK
        string name
        string slug UK
        image icon
        text description
        int article_count
    }
    
    Tag {
        int id PK
        string name
        string slug UK
    }
    
    Article {
        int id PK
        string title
        string slug UK
        text summary
        richtext content
        image featured_image
        int category_id FK
        int author_id FK
        string status
        bool is_breaking
        bool is_featured
        int views_count
        datetime published_at
    }
    
    Video {
        int id PK
        string title
        string slug UK
        text description
        image thumbnail
        string video_url
        int category_id FK
        int author_id FK
        string duration
        int views_count
        bool is_featured
        bool is_active
        datetime published_at
    }
    
    Comment {
        int id PK
        int article_id FK
        int user_id FK
        text content
        bool is_approved
        datetime created_at
    }
    
    BreakingNews {
        int id PK
        string text
        bool urgent
        bool is_active
        datetime created_at
    }
    
    NewsletterSubscriber {
        int id PK
        string email UK
        bool is_active
        datetime subscribed_at
        datetime unsubscribed_at
    }
```

## Requirements
- Python 3.11+ (recommended: 3.13)
- pip
- SQLite (default) or PostgreSQL/MySQL (optional)

## Installation
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the backend directory:
```
SECRET_KEY=your-strong-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:5500
```

### Optional (Production)
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

## Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser
```bash
python manage.py createsuperuser
```

## Run Development Server
```bash
python manage.py runserver
```

## Admin Access
- URL: `http://127.0.0.1:8000/admin/`
- Use the superuser created above.

## API Documentation
- Full API reference: [docs/API.md](docs/API.md)
- Base URL: `http://127.0.0.1:8000/api/`

## Production Deployment Checklist

### Security Settings
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY` (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS and update `CSRF_TRUSTED_ORIGINS` with https:// URLs
- [ ] Enable secure cookies: `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`

### Database
- [ ] Migrate from SQLite to PostgreSQL/MySQL for production
- [ ] Set up database backups
- [ ] Configure connection pooling

### Static & Media Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure cloud storage (AWS S3, Cloudinary) for media files
- [ ] Set up CDN for static assets

### Performance
- [ ] Enable caching (Redis/Memcached)
- [ ] Configure database query optimization
- [ ] Set up Gunicorn/uWSGI as WSGI server
- [ ] Configure Nginx as reverse proxy

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Enable Django Admin email notifications for errors

### Environment Variables (Production)
```env
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Common API Endpoints (Summary)
- `GET /api/articles/`
- `GET /api/articles/<slug>/`
- `GET /api/articles/trending/`
- `GET /api/articles/featured/`
- `GET /api/articles/most-commented/`
- `GET /api/categories/`
- `GET /api/tags/`
- `GET /api/breaking-news/`
- `GET /api/search/?q=...`
- `GET/POST /api/comments/`
- `POST /api/newsletter/subscribe/`
- `POST /api/newsletter/unsubscribe/`

## Sample Data (Optional)
```bash
python manage.py populate_sample_data
# or
python manage.py populate_sample_data --flush --articles 50
```

## Media Files
- Uploaded files are stored in `backend/media/` (development).
- Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured in settings.

## Docker (Optional)
```bash
# From repository root
docker compose up --build
```

For development with auto-reload, override the command in `docker-compose.yml`:
```yaml
command: python manage.py runserver 0.0.0.0:8000
```

## Automated Setup Script
```bash
# From repository root
bash backend/scripts/setup.sh
```

## Troubleshooting
- If `manage.py check --deploy` shows warnings, ensure HTTPS/secure settings in production.
- If images are not served, verify `MEDIA_URL` and `MEDIA_ROOT` and your web server config.
