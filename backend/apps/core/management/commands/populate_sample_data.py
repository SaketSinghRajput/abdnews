"""
Management command to populate the database with sample data.

Usage:
    python manage.py populate_sample_data
    python manage.py populate_sample_data --flush  # Clear existing data first
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from apps.news.models import Category, Tag, Article, Comment, BreakingNews, NewsletterSubscriber
from apps.users.models import Author
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before populating',
        )
        parser.add_argument(
            '--articles',
            type=int,
            default=20,
            help='Number of articles to create (default: 20)',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            self.flush_data()

        with transaction.atomic():
            self.stdout.write('Creating sample data...')
            
            # Create users and authors
            users, authors = self.create_users_and_authors()
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(users)} users and {len(authors)} authors'))
            
            # Create categories
            categories = self.create_categories()
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories)} categories'))
            
            # Create tags
            tags = self.create_tags()
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(tags)} tags'))
            
            # Create articles
            articles = self.create_articles(authors, categories, tags, count=options['articles'])
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(articles)} articles'))
            
            # Create comments
            comments = self.create_comments(users, articles)
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(comments)} comments'))
            
            # Create breaking news
            breaking_news = self.create_breaking_news(articles)
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(breaking_news)} breaking news items'))
            
            # Create newsletter subscribers
            subscribers = self.create_newsletter_subscribers()
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(subscribers)} newsletter subscribers'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Sample data populated successfully!'))

    def flush_data(self):
        """Delete all existing data."""
        Comment.objects.all().delete()
        BreakingNews.objects.all().delete()
        Article.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        NewsletterSubscriber.objects.all().delete()
        Author.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users_and_authors(self):
        """Create sample users and author profiles."""
        users = []
        authors = []
        
        # Create admin user
        if not User.objects.filter(email='admin@newshub.com').exists():
            admin = User.objects.create_superuser(
                email='admin@newshub.com',
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            users.append(admin)
        
        # Create editor users
        editor_data = [
            ('editor@newshub.com', 'editor1', 'Jane', 'Smith', 'Senior Editor'),
            ('editor2@newshub.com', 'editor2', 'Mike', 'Johnson', 'Tech Editor'),
        ]
        
        for email, username, first_name, last_name, designation in editor_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role='editor'
                )
                users.append(user)
        
        # Create journalist users with author profiles
        journalist_data = [
            ('john.doe@newshub.com', 'johndoe', 'John', 'Doe', 'Senior Journalist',
             'Experienced journalist covering technology and business news.'),
            ('sarah.wilson@newshub.com', 'sarahwilson', 'Sarah', 'Wilson', 'Political Correspondent',
             'Political analyst with 10+ years of experience in investigative journalism.'),
            ('david.brown@newshub.com', 'davidbrown', 'David', 'Brown', 'Sports Reporter',
             'Sports enthusiast covering major leagues and international tournaments.'),
            ('emily.davis@newshub.com', 'emilydavis', 'Emily', 'Davis', 'Entertainment Writer',
             'Pop culture expert reporting on movies, music, and celebrity news.'),
            ('michael.taylor@newshub.com', 'michaeltaylor', 'Michael', 'Taylor', 'Science Correspondent',
             'Science journalist passionate about climate change and space exploration.'),
        ]
        
        for email, username, first_name, last_name, designation, bio in journalist_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role='journalist'
                )
                users.append(user)
                
                # Create author profile
                author = Author.objects.create(
                    user=user,
                    designation=designation,
                    bio=bio,
                    twitter_url=f"https://twitter.com/{username}",
                    linkedin_url=f"https://linkedin.com/in/{username}",
                )
                authors.append(author)
        
        # Create some regular users (for comments)
        for i in range(5):
            email = f'user{i+1}@example.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    username=f'user{i+1}',
                    password='password123',
                    first_name=f'User',
                    last_name=f'{i+1}',
                    role='journalist'
                )
                users.append(user)
        
        return users, authors

    def create_categories(self):
        """Create sample categories."""
        category_data = [
            ('Technology', 'Latest tech news, gadgets, and innovations'),
            ('Business', 'Business news, markets, and economy updates'),
            ('Politics', 'Political news and government updates'),
            ('Sports', 'Sports news, scores, and highlights'),
            ('Entertainment', 'Entertainment news, movies, and music'),
            ('Science', 'Scientific discoveries and research'),
            ('Health', 'Health tips, medical news, and wellness'),
            ('World', 'International news from around the globe'),
            ('Lifestyle', 'Lifestyle, fashion, and culture'),
            ('Opinion', 'Editorial opinions and analysis'),
        ]
        
        categories = []
        for name, description in category_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories.append(category)
        
        return categories

    def create_tags(self):
        """Create sample tags."""
        tag_names = [
            'Breaking News', 'Trending', 'Featured', 'Analysis', 'Interview',
            'Investigation', 'Opinion', 'Review', 'Guide', 'Tutorial',
            'AI', 'Climate Change', 'COVID-19', 'Elections', 'Olympics',
            'Cryptocurrency', 'Startup', 'IPO', 'Market', 'Innovation',
        ]
        
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        
        return tags

    def create_articles(self, authors, categories, tags, count=20):
        """Create sample articles."""
        if not authors:
            self.stdout.write(self.style.WARNING('No authors available. Skipping articles.'))
            return []
        
        article_templates = [
            {
                'title': 'Artificial Intelligence Breakthrough: New Model Surpasses Human Performance',
                'summary': 'Researchers announce a groundbreaking AI model that achieves unprecedented accuracy in complex reasoning tasks.',
                'content': '''<p>In a major breakthrough for artificial intelligence research, scientists at a leading tech institute have developed a new AI model that surpasses human performance in several complex reasoning tasks.</p>
                
                <p>The model, which uses a novel architecture combining transformer networks with reinforcement learning, demonstrated remarkable capabilities in mathematical problem-solving, logical reasoning, and even creative tasks.</p>
                
                <h2>Key Achievements</h2>
                <ul>
                    <li>98% accuracy on advanced mathematics problems</li>
                    <li>Superior performance in multi-step reasoning tasks</li>
                    <li>Ability to explain its reasoning process in natural language</li>
                </ul>
                
                <p>This development marks a significant milestone in the pursuit of artificial general intelligence and opens up new possibilities for AI applications across various industries.</p>''',
            },
            {
                'title': 'Global Markets Rally as Economic Indicators Show Strong Recovery',
                'summary': 'Stock markets worldwide experience significant gains following positive economic data releases.',
                'content': '''<p>Global financial markets experienced a strong rally today as key economic indicators pointed to a robust recovery in major economies.</p>
                
                <p>The S&P 500 surged 2.5%, while European and Asian markets also posted substantial gains. Investors responded positively to better-than-expected employment figures and consumer confidence data.</p>
                
                <h2>Market Performance</h2>
                <p>Major indices saw significant movement:</p>
                <ul>
                    <li>S&P 500: +2.5%</li>
                    <li>NASDAQ: +3.1%</li>
                    <li>FTSE 100: +1.8%</li>
                    <li>Nikkei 225: +2.2%</li>
                </ul>
                
                <p>Analysts suggest this trend could continue if economic fundamentals remain strong.</p>''',
            },
            {
                'title': 'Climate Summit Reaches Historic Agreement on Carbon Emissions',
                'summary': 'World leaders commit to ambitious carbon reduction targets in landmark climate agreement.',
                'content': '''<p>In a historic development, leaders from over 190 countries have reached a comprehensive agreement on carbon emission reductions at this year\'s climate summit.</p>
                
                <p>The agreement includes binding commitments to achieve net-zero emissions by 2050 and intermediate targets for 2030.</p>
                
                <h2>Key Commitments</h2>
                <ul>
                    <li>50% reduction in emissions by 2030</li>
                    <li>$100 billion annual climate finance for developing nations</li>
                    <li>Phase out of coal power by 2035</li>
                    <li>Protection of 30% of land and ocean areas</li>
                </ul>
                
                <p>Environmental groups have cautiously welcomed the agreement while emphasizing the need for rapid implementation.</p>''',
            },
        ]
        
        articles = []
        now = timezone.now()
        
        for i in range(count):
            template = article_templates[i % len(article_templates)]
            
            # Create unique title for each article
            title = f"{template['title']} - Part {i+1}" if i >= len(article_templates) else template['title']
            
            article = Article.objects.create(
                title=title,
                summary=template['summary'],
                content=template['content'],
                author=random.choice(authors),
                category=random.choice(categories),
                status='published',
                is_featured=random.random() > 0.7,  # 30% chance of being featured
                views_count=random.randint(100, 5000),
                published_at=now - timedelta(days=random.randint(0, 30)),
            )
            
            # Add random tags (2-5 tags per article)
            article_tags = random.sample(tags, k=random.randint(2, 5))
            article.tags.set(article_tags)
            
            articles.append(article)
        
        return articles

    def create_comments(self, users, articles):
        """Create sample comments."""
        if not users or not articles:
            return []
        
        comment_texts = [
            "Great article! Very informative and well-written.",
            "I disagree with some of the points made here, but overall a good read.",
            "Thanks for sharing this. It helped me understand the topic better.",
            "Could you provide more sources for these claims?",
            "Interesting perspective. I hadn't thought about it this way before.",
            "This is exactly what I was looking for. Thank you!",
            "Well researched and presented. Keep up the good work!",
            "I have a different opinion on this matter...",
        ]
        
        comments = []
        
        # Create 2-5 comments for some articles
        for article in random.sample(articles, k=min(len(articles), 15)):
            num_comments = random.randint(2, 5)
            for _ in range(num_comments):
                comment = Comment.objects.create(
                    article=article,
                    user=random.choice(users),
                    content=random.choice(comment_texts),
                    is_approved=random.random() > 0.2,  # 80% approval rate
                )
                comments.append(comment)
        
        return comments

    def create_breaking_news(self, articles):
        """Create breaking news items."""
        if not articles:
            return []
        
        breaking_news_items = []
        
        # Select 2-3 recent articles as breaking news
        recent_articles = sorted(articles, key=lambda x: x.published_at, reverse=True)[:3]
        
        for article in recent_articles:
            breaking = BreakingNews.objects.create(
                text=article.title,
                urgent=True,
                is_active=True,
            )
            breaking_news_items.append(breaking)
        
        return breaking_news_items

    def create_newsletter_subscribers(self):
        """Create newsletter subscribers."""
        emails = [
            'subscriber1@example.com',
            'subscriber2@example.com',
            'subscriber3@example.com',
            'subscriber4@example.com',
            'subscriber5@example.com',
            'inactive@example.com',  # This one will be inactive
        ]
        
        subscribers = []
        for i, email in enumerate(emails):
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': i < len(emails) - 1}  # Last one is inactive
            )
            subscribers.append(subscriber)
        
        return subscribers
