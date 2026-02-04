# Quick Testing Guide

## Prerequisites
- Django server running: `python manage.py runserver`
- Admin access: http://127.0.0.1:8000/admin/

## Quick Tests

### 1. Site Settings (Logo & Name)
```
1. Go to Admin > Core > Site Settings
2. Change "Site Name" to "MyNews"
3. Save
4. Refresh http://127.0.0.1:8000/index.html
✅ Header should show "MyNews"
```

### 2. Social Links (Footer)
```
1. Go to Admin > Core > Social Links
2. Add new social link:
   - Platform: Facebook
   - URL: https://facebook.com/mynews
   - Icon: fab fa-facebook-f
3. Save
4. Refresh frontend
✅ Footer should show Facebook icon with link
```

### 3. Homepage Section
```
1. Go to Admin > Core > Homepage Sections
2. Create new section:
   - Title: "Top Stories"
   - Section Type: Featured
   - Position: 10
   - Status: Active
3. In "Articles" tab, add 2-3 articles
4. Save
5. Refresh homepage
✅ "Top Stories" section appears with articles
```

### 4. Advertisement
```
1. Go to Admin > Core > Advertisement Banners
2. Create new ad:
   - Title: "Special Offer"
   - Position: Sidebar
   - Link URL: https://example.com
   - Upload image
   - Is Active: ✓
3. Save
4. Refresh frontend
✅ Ad appears in left sidebar
```

### 5. SEO Settings
```
1. Go to Admin > Core > SEO Settings
2. Change "Meta Title" to "MyNews - Latest Updates"
3. Save
4. Refresh frontend
5. Right-click > View Page Source
✅ <title> shows "MyNews - Latest Updates"
```

### 6. Breaking News
```
1. Go to Admin > News > Breaking News
2. Create new:
   - Text: "URGENT: Breaking news update"
   - Display Until: [future date]
3. Save
4. Refresh frontend
✅ Ticker shows "URGENT: Breaking news update"
```

## API Endpoints to Verify

Visit these URLs in browser to check API responses:

1. Site Settings: http://127.0.0.1:8000/api/site-settings/
2. Social Links: http://127.0.0.1:8000/api/social-links/
3. Homepage Sections: http://127.0.0.1:8000/api/homepage/
4. Advertisements: http://127.0.0.1:8000/api/ads/?position=sidebar
5. Categories: http://127.0.0.1:8000/api/news/categories/
6. Articles: http://127.0.0.1:8000/api/news/articles/
7. Breaking News: http://127.0.0.1:8000/api/news/breaking-news/

Each should return JSON data without errors.

## Browser Console

Open Developer Tools (F12) > Console tab:
- No red errors
- Should see: "NewsHub initialized successfully!"

## Expected Behavior

### On Page Load:
1. Loading spinner appears
2. API requests fired (check Network tab)
3. Content populates dynamically
4. Loading spinner disappears

### On Admin Change:
1. Make change in admin
2. Save
3. Refresh frontend
4. See change immediately

## Common Issues

### No content shows:
- Check backend is running
- Check APIs return data (visit URLs above)
- Check browser console for errors

### Images broken:
- Ensure MEDIA_URL configured
- Check image uploaded in admin
- Verify image URL in API response

### Loading never finishes:
- Check API errors in console
- Verify backend accessible
- Check network requests failed

## Success Criteria

✅ Header shows dynamic logo and navigation
✅ Footer shows dynamic social links and copyright
✅ Homepage sections render from CMS
✅ Sidebar shows dynamic categories
✅ Breaking news ticker works
✅ All images load with correct URLs
✅ Navigation links work
✅ Loading states appear/disappear
✅ Admin changes reflect on refresh
✅ No console errors

## Demo Workflow

1. Start backend: `python manage.py runserver`
2. Login to admin: http://127.0.0.1:8000/admin/
3. Create sample content:
   - 5-10 articles with images
   - 2-3 categories
   - 2-3 social links
   - 1 homepage section
   - 1 sidebar ad
4. Open frontend: http://127.0.0.1:8000/index.html
5. Verify all content appears dynamically
6. Make changes in admin
7. Refresh frontend
8. See updates immediately

**Status**: Frontend is 100% dynamic! 🚀
