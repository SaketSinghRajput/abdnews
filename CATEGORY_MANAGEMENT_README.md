# Category Management System

## Overview
Complete category and subcategory management system with real-time frontend updates for NewsHub.

## Features

### ✅ Backend Features
- **Hierarchical Categories**: Support for main categories and unlimited subcategories
- **Category Properties**:
  - Name and unique slug (auto-generated)
  - Parent category (for subcategories)
  - Custom color (hex format)
  - Icon/image upload
  - Description
  - Active/Inactive status
  - Display order
  - Article count (auto-updated)
- **Django Admin Integration**: Full CRUD operations in admin panel
- **RESTful API Endpoints**:
  - Public endpoints (read-only)
  - Admin-only endpoints (full CRUD)
  - Category tree endpoint for hierarchical data
  - Reorder endpoint for drag-drop support

### ✅ Frontend Features
- **Admin Panel** (`/pages/admin-categories.html`):
  - Create, edit, and delete categories/subcategories
  - Visual category cards with color badges
  - Real-time article count display
  - Active/inactive status toggle
  - Display order management
  - Parent category selection for subcategories
- **Real-Time Updates**:
  - Categories refresh every 60 seconds
  - Navigation menu updates automatically
  - No page refresh needed for category changes
- **Dynamic Navigation**:
  - Categories load dynamically in header
  - Color-coded category links
  - Hierarchical subcategory display

## API Endpoints

### Public Endpoints
```
GET /api/news/categories/              # List all active categories
GET /api/news/categories/tree/         # Hierarchical category tree
GET /api/news/categories/{slug}/       # Get single category by slug
```

### Admin-Only Endpoints (Requires Authentication)
```
GET    /api/news/admin/categories/           # List all categories (including inactive)
POST   /api/news/admin/categories/           # Create new category
GET    /api/news/admin/categories/{id}/      # Get category by ID
PUT    /api/news/admin/categories/{id}/      # Update category
DELETE /api/news/admin/categories/{id}/      # Delete category
POST   /api/news/admin/categories/reorder/   # Reorder categories
```

## Usage

### Creating a Category
1. Login as admin
2. Navigate to `/pages/admin-categories.html`
3. Click "+ Add Category" button
4. Fill in:
   - **Name**: Category name (e.g., "Technology")
   - **Parent Category**: Leave empty for main category, or select parent for subcategory
   - **Color**: Choose a color (default: #3b82f6)
   - **Description**: Optional description
   - **Display Order**: Number (lower = appears first)
   - **Active**: Check to make visible on website
5. Click "Save Category"

### Creating a Subcategory
1. Follow steps 1-4 above
2. In **Parent Category** dropdown, select a main category
3. Save

### Editing a Category
1. Click "Edit" button on any category card
2. Modify fields
3. Click "Save Category"

### Deleting a Category
1. Click "Delete" button
2. Confirm deletion
3. **Note**: Cannot delete categories with:
   - Existing articles (reassign first)
   - Subcategories (delete subcategories first)

### Real-Time Navigation Updates
- Categories automatically appear in header navigation
- Changes reflect within 60 seconds
- Color-coded category links
- Article counts visible in admin panel

## Database Schema

### Category Model
```python
class Category(models.Model):
    name = CharField(max_length=100)              # Category name
    slug = SlugField(unique=True)                 # URL-friendly slug
    parent = ForeignKey('self', null=True)        # Parent category
    icon = ImageField(blank=True)                 # Category icon
    color = CharField(max_length=7, default='#3b82f6')  # Hex color
    description = TextField(blank=True)           # Description
    article_count = PositiveIntegerField(default=0)     # Article count
    is_active = BooleanField(default=True)        # Active status
    order = PositiveIntegerField(default=0)       # Display order
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Files Modified/Created

### Backend
- ✅ `backend/apps/news/models.py` - Added parent, color, is_active, order fields
- ✅ `backend/apps/news/serializers.py` - Added CategoryTreeSerializer
- ✅ `backend/apps/news/views.py` - Added admin management views
- ✅ `backend/apps/news/urls.py` - Added admin API routes
- ✅ `backend/apps/news/admin.py` - Enhanced admin interface
- ✅ Migration: `0006_alter_category_options_category_color_and_more.py`

### Frontend
- ✅ `frontend/pages/admin-categories.html` - Admin management UI
- ✅ `frontend/assets/js/categories.js` - Category manager module
- ✅ `frontend/assets/js/app.js` - Added admin link in auth buttons
- ✅ `frontend/components/header.html` - Dynamic category loading

## Testing

### Manual Testing Steps
1. **Create Main Category**:
   - Login as admin
   - Go to admin-categories.html
   - Create "Technology" category with blue color
   - Verify it appears in header within 60 seconds

2. **Create Subcategory**:
   - Create "AI & ML" subcategory under Technology
   - Verify it shows under Technology in admin panel

3. **Edit Category**:
   - Change Technology color to green
   - Verify color updates in header navigation

4. **Delete Category**:
   - Try deleting category with articles (should fail)
   - Delete empty category (should succeed)

5. **Real-Time Updates**:
   - Open site in two browser windows
   - Create category in one window
   - Watch it appear in other window within 60 seconds

## Permissions
- **Public**: View active categories and articles
- **Admin/Staff**: Full CRUD on all categories
- **Authentication**: Required for admin endpoints

## Security
- Admin endpoints protected with `IsAdminUser` permission
- CSRF protection on POST/PUT/DELETE
- JWT authentication required
- Input validation and sanitization

## Performance
- Categories cached for 60 seconds on frontend
- Efficient queries with select_related/prefetch_related
- Pagination support on list endpoints
- Optimized for up to 1000+ categories

## Future Enhancements
- [ ] Drag-and-drop reordering in UI
- [ ] Bulk category operations
- [ ] Category analytics dashboard
- [ ] Category merging functionality
- [ ] Multi-level subcategory support (currently 2 levels)
- [ ] Category import/export
- [ ] Category templates

## Troubleshooting

### Categories not showing in navigation
- Check if categories are marked as active
- Clear browser cache
- Check browser console for JavaScript errors
- Verify API endpoint returns data

### Cannot delete category
- Ensure category has no articles
- Ensure category has no subcategories
- Check user has admin permissions

### Colors not displaying
- Verify color is valid hex format (#RRGGBB)
- Check CSS styles are loaded
- Clear browser cache

## API Examples

### Get Category Tree
```bash
curl http://localhost:8000/api/news/categories/tree/
```

### Create Category (Admin)
```bash
curl -X POST http://localhost:8000/api/news/admin/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology",
    "color": "#3b82f6",
    "description": "Latest tech news",
    "is_active": true,
    "order": 0
  }'
```

### Update Category (Admin)
```bash
curl -X PUT http://localhost:8000/api/news/admin/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech & Innovation",
    "color": "#10b981"
  }'
```

## Support
For issues or questions, contact the development team.
