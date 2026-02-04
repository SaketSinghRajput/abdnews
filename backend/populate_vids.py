from apps.news.models import Video, Category
from apps.users.models import Author

tech_cat, _ = Category.objects.get_or_create(slug='technology', defaults={'name': 'Technology', 'icon': 'fas fa-laptop'})
business_cat, _ = Category.objects.get_or_create(slug='business', defaults={'name': 'Business', 'icon': 'fas fa-briefcase'})
entertainment_cat, _ = Category.objects.get_or_create(slug='entertainment', defaults={'name': 'Entertainment', 'icon': 'fas fa-film'})

author = Author.objects.first()

videos = [
    {'title': 'AI Revolution: The Future of Technology', 'description': 'Exploring how artificial intelligence is transforming industries and our daily lives.', 'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'duration': '12:45', 'category': tech_cat, 'is_featured': True, 'views': 2500},
    {'title': 'Startup Success Stories', 'description': 'Learn from entrepreneurs who turned their ideas into million-dollar companies.', 'video_url': 'https://www.youtube.com/embed/jNQXAC9IVRw', 'duration': '18:20', 'category': business_cat, 'is_featured': True, 'views': 1800},
    {'title': 'Bollywood Behind the Scenes', 'description': 'Get an exclusive look at how Bollywood movies are made.', 'video_url': 'https://www.youtube.com/embed/9bZkp7q19f0', 'duration': '15:30', 'category': entertainment_cat, 'is_featured': True, 'views': 3200},
    {'title': 'Crypto Trading Guide', 'description': 'A beginner guide to cryptocurrency trading and blockchain.', 'video_url': 'https://www.youtube.com/embed/QCvL-UMvnzo', 'duration': '22:15', 'category': business_cat, 'is_featured': False, 'views': 1200},
    {'title': 'Cloud Computing Explained', 'description': 'Understanding cloud computing: AWS, Azure, Google Cloud.', 'video_url': 'https://www.youtube.com/embed/Mvhw9Oy6suc', 'duration': '16:50', 'category': tech_cat, 'is_featured': False, 'views': 950},
    {'title': 'Influencer Marketing Trends 2024', 'description': 'What\'s next in influencer marketing and content creation?', 'video_url': 'https://www.youtube.com/embed/XGSy3_Czjk0', 'duration': '14:10', 'category': entertainment_cat, 'is_featured': False, 'views': 1450},
]

for v_data in videos:
    views = v_data.pop('views')
    v, created = Video.objects.get_or_create(title=v_data['title'], defaults={**v_data, 'author': author, 'views_count': views})
    if created:
        print(f"✓ {v.title}")
    else:
        print(f"- {v.title} (exists)")

print(f"\nTotal videos: {Video.objects.count()}")
