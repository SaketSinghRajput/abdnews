"""
Populate video data for NewsHub.

Run with: python manage.py shell < scripts/populate_videos.py
"""

from apps.news.models import Video, Category
from apps.users.models import Author
from django.utils import timezone

# Get or create categories
tech_category, _ = Category.objects.get_or_create(
    slug='technology',
    defaults={
        'name': 'Technology',
        'icon': 'fas fa-laptop',
        'description': 'Tech news and insights'
    }
)

business_category, _ = Category.objects.get_or_create(
    slug='business',
    defaults={
        'name': 'Business',
        'icon': 'fas fa-briefcase',
        'description': 'Business and market news'
    }
)

entertainment_category, _ = Category.objects.get_or_create(
    slug='entertainment',
    defaults={
        'name': 'Entertainment',
        'icon': 'fas fa-film',
        'description': 'Entertainment and celebrities'
    }
)

# Get a default author
author = Author.objects.first()

# Demo videos data
videos_data = [
    {
        'title': 'AI Revolution: The Future of Technology',
        'description': 'Exploring how artificial intelligence is transforming industries and our daily lives. In this comprehensive video, we dive into the latest AI breakthroughs, machine learning applications, and what the future holds for tech enthusiasts.',
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'duration': '12:45',
        'category': tech_category,
        'is_featured': True,
        'views_count': 2500,
    },
    {
        'title': 'Startup Success Stories',
        'description': 'Learn from entrepreneurs who turned their ideas into million-dollar companies. This video features interviews with successful startup founders sharing their journey, challenges, and lessons learned.',
        'video_url': 'https://www.youtube.com/embed/jNQXAC9IVRw',
        'duration': '18:20',
        'category': business_category,
        'is_featured': True,
        'views_count': 1800,
    },
    {
        'title': 'Bollywood Behind the Scenes',
        'description': 'Get an exclusive look at how Bollywood movies are made. From script writing to final editing, discover the magic behind the scenes of Indian cinema.',
        'video_url': 'https://www.youtube.com/embed/9bZkp7q19f0',
        'duration': '15:30',
        'category': entertainment_category,
        'is_featured': True,
        'views_count': 3200,
    },
    {
        'title': 'Crypto Trading Guide',
        'description': 'A beginner\'s guide to cryptocurrency trading. Learn about blockchain, wallets, exchanges, and how to make your first crypto investment safely.',
        'video_url': 'https://www.youtube.com/embed/QCvL-UMvnzo',
        'duration': '22:15',
        'category': business_category,
        'is_featured': False,
        'views_count': 1200,
    },
    {
        'title': 'Cloud Computing Explained',
        'description': 'Understanding cloud computing: AWS, Azure, Google Cloud. A deep dive into how businesses are migrating to the cloud and the benefits it offers.',
        'video_url': 'https://www.youtube.com/embed/Mvhw9Oy6suc',
        'duration': '16:50',
        'category': tech_category,
        'is_featured': False,
        'views_count': 950,
    },
    {
        'title': 'Influencer Marketing Trends 2024',
        'description': 'What\'s next in influencer marketing? Explore the latest trends, strategies, and how brands are collaborating with content creators.',
        'video_url': 'https://www.youtube.com/embed/XGSy3_Czjk0',
        'duration': '14:10',
        'category': entertainment_category,
        'is_featured': False,
        'views_count': 1450,
    },
    {
        'title': 'Stock Market Basics',
        'description': 'Everything you need to know to start investing in the stock market. Learn about different types of stocks, how to pick winners, and build your portfolio.',
        'video_url': 'https://www.youtube.com/embed/oBt53YbSK_o',
        'duration': '19:45',
        'category': business_category,
        'is_featured': False,
        'views_count': 2100,
    },
    {
        'title': 'Web Development 2024',
        'description': 'Latest web development frameworks and technologies. From React to Vue, learn what\'s trending in web development and how to stay updated.',
        'video_url': 'https://www.youtube.com/embed/D6Ll_nzx77c',
        'duration': '21:20',
        'category': tech_category,
        'is_featured': False,
        'views_count': 1680,
    },
]

# Create videos
created_count = 0
for video_data in videos_data:
    video, created = Video.objects.get_or_create(
        title=video_data['title'],
        defaults={
            **video_data,
            'author': author,
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created video: {video.title}")
    else:
        print(f"- Video already exists: {video.title}")

print(f"\nTotal videos created: {created_count}")
