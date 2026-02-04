# Testing Guide

## Running Tests
```bash
python manage.py test
```

## Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## API Testing with Postman

Import the Postman collection from `docs/NewsHub.postman_collection.json`.

### Test Scenarios
1. **Article CRUD** - Create, read, update, delete articles
2. **Authentication** - Login, logout, token validation
3. **Search** - Full-text search across articles
4. **Filtering** - Category, tag, featured, breaking filters
5. **Pagination** - Page navigation and page_size limits
6. **Comments** - Create and moderate comments
7. **Newsletter** - Subscribe and unsubscribe

## Manual Testing Checklist
- [ ] Admin login and dashboard access
- [ ] Article creation with rich text editor
- [ ] Image upload and preview
- [ ] Category and tag management
- [ ] Comment moderation
- [ ] Breaking news activation
- [ ] Newsletter subscription
- [ ] API endpoint responses
- [ ] CORS configuration
- [ ] View counter functionality
