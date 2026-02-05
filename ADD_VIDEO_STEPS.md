# How to Add Featured Videos on EC2

## The Issue
The "Bihar Boy Kand" video you see in the admin screenshot was not actually saved to the database. You need to follow these steps to properly add and save it.

## Steps to Add a Featured Video

### 1. Access Django Admin on EC2
Go to: `http://3.235.243.73/admin/news/video/`

### 2. Click "Add Video" Button
In the top right corner, click the green "ADD VIDEO +" button

### 3. Fill in the Video Form
**Required Fields:**
- **Title**: Bihar Boy Kand (or whatever you want)
- **Video URL**: The actual URL to the video (YouTube, Vimeo, etc.)
  - Example: `https://www.youtube.com/watch?v=xxxxx`
  - Or: `https://vimeo.com/xxxxx`

**Optional but Recommended:**
- **Category**: Select a category (Politics, Entertainment, etc.)
- **Author**: Select an author (or leave as Unassigned)
- **Duration**: e.g., "5:30" for 5 minutes 30 seconds
- **Thumbnail**: Upload an image for the video thumbnail
- **Description**: Brief description of the video

**Important - Check These Boxes:**
- ✅ **Is featured** - MUST be checked to show in Featured Videos section
- ✅ **Is active** - MUST be checked for video to be visible

### 4. Click "SAVE" Button
At the bottom right, click the blue "SAVE" button

### 5. Verify the Video was Saved
After saving, you should see:
- A success message: "The video "Bihar Boy Kand" was added successfully."
- The video in the list with a proper ID number

### 6. Test the API
Check if the video appears in the API:
```bash
curl http://3.235.243.73/api/news/videos/featured/
```

### 7. Refresh the Homepage
Go to: `http://3.235.243.73/`
Scroll to "Featured Videos" section - your video should now appear!

## Common Mistakes to Avoid
❌ **Don't just browse the video list** - that won't add a video
❌ **Don't forget to check "Is featured"** - without this, it won't show
❌ **Don't forget to check "Is active"** - without this, it won't be visible
❌ **Don't forget to click SAVE** - the video isn't saved until you click SAVE

## Quick Add Video via Django Shell (Alternative Method)

If you want to quickly add a test video via command line:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@3.235.243.73

# Navigate to project
cd /home/ubuntu/newshub/backend
source /home/ubuntu/newshub/venv/bin/activate

# Add video via Django shell
python manage.py shell

# In the shell, run:
from apps.news.models import Video, Category, Author
from django.utils.text import slugify

# Create the video
video = Video.objects.create(
    title="Bihar Boy Kand",
    slug=slugify("Bihar Boy Kand"),
    description="Description of the video",
    video_url="https://www.youtube.com/watch?v=example",
    duration="5:30",
    is_featured=True,  # IMPORTANT!
    is_active=True     # IMPORTANT!
)

print(f"Created video: {video.title} (ID: {video.id})")
```

## Verify Changes
After adding the video, verify it appears:

1. **Check in Admin**: Should see the video in the list with ID
2. **Check API**: `curl http://3.235.243.73/api/news/videos/featured/`
3. **Check Homepage**: Visit homepage and scroll to Featured Videos

## Need More Featured Videos?
To add more featured videos:
1. Repeat the steps above for each video
2. Make sure each has `is_featured=True` and `is_active=True`
3. The carousel will automatically show all featured videos
