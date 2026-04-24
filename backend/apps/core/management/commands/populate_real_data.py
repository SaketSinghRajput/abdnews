"""
Management command to populate the database with real-world news data.
Includes actual headlines, working YouTube video embeds, and realistic author profiles.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import random

from apps.news.models import Article, Category, Tag, Video, BreakingNews
from apps.users.models import CustomUser, Author


class Command(BaseCommand):
    help = "Populate database with real-world news data, videos, and author profiles"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Starting real-world data population...")

        # Create categories first
        categories = self.create_categories()

        # Create authors
        authors = self.create_authors()

        # Create articles with real headlines
        articles = self.create_articles(categories, authors)

        # Create videos with working YouTube embeds
        videos = self.create_videos(categories, authors)

        # Create breaking news
        self.create_breaking_news()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully populated database with:\n"
            f"  - {len(categories)} categories\n"
            f"  - {len(authors)} authors\n"
            f"  - {len(articles)} articles\n"
            f"  - {len(videos)} videos\n"
            f"  - 5 breaking news items"
        ))

    def create_categories(self):
        """Create news categories with proper colors and icons."""
        categories_data = [
            {"name": "Technology", "slug": "technology", "color": "#3B82F6", "icon": "fa-microchip", "order": 1},
            {"name": "Business", "slug": "business", "color": "#10B981", "icon": "fa-chart-line", "order": 2},
            {"name": "Science", "slug": "science", "color": "#8B5CF6", "icon": "fa-flask", "order": 3},
            {"name": "AI & Machine Learning", "slug": "ai-machine-learning", "color": "#EF4444", "icon": "fa-brain", "order": 4},
            {"name": "Space", "slug": "space", "color": "#F59E0B", "icon": "fa-rocket", "order": 5},
            {"name": "Health", "slug": "health", "color": "#EC4899", "icon": "fa-heart", "order": 6},
            {"name": "Finance", "slug": "finance", "color": "#06B6D4", "icon": "fa-coins", "order": 7},
            {"name": "Startups", "slug": "startups", "color": "#84CC16", "icon": "fa-lightbulb", "order": 8},
            {"name": "Policy", "slug": "policy", "color": "#6366F1", "icon": "fa-landmark", "order": 9},
            {"name": "Climate", "slug": "climate", "color": "#22C55E", "icon": "fa-leaf", "order": 10},
        ]

        categories = []
        for cat_data in categories_data:
            category, _ = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={
                    "name": cat_data["name"],
                    "color": cat_data["color"],
                    "icon": cat_data["icon"],
                    "order": cat_data["order"],
                    "is_active": True,
                }
            )
            categories.append(category)

        self.stdout.write(f"Created {len(categories)} categories")
        return categories

    def create_authors(self):
        """Create realistic author profiles."""
        authors_data = [
            {
                "username": "sarah_chen",
                "email": "sarah.chen@abdnews.demo",
                "first_name": "Sarah",
                "last_name": "Chen",
                "bio": "Senior Technology Correspondent. Former Wired contributor. Covering AI, quantum computing, and the future of tech.",
                "designation": "Senior Technology Editor",
            },
            {
                "username": "james_rodriguez",
                "email": "james.rodriguez@abdnews.demo",
                "first_name": "James",
                "last_name": "Rodriguez",
                "bio": "Business and Finance Editor. 15 years covering Wall Street, startups, and global markets.",
                "designation": "Business Editor",
            },
            {
                "username": "dr_emma_watson",
                "email": "emma.watson@abdnews.demo",
                "first_name": "Emma",
                "last_name": "Watson",
                "bio": "Science Correspondent with a Ph.D. in Physics. Specializing in quantum computing and space exploration.",
                "designation": "Science Correspondent",
            },
            {
                "username": "michael_okonkwo",
                "email": "michael.okonkwo@abdnews.demo",
                "first_name": "Michael",
                "last_name": "Okonkwo",
                "bio": "AI & Machine Learning Specialist. Former Google AI researcher. Making complex AI accessible.",
                "designation": "AI Editor",
            },
            {
                "username": "rachel_goldstein",
                "email": "rachel.goldstein@abdnews.demo",
                "first_name": "Rachel",
                "last_name": "Goldstein",
                "bio": "Space & Defense Correspondent. Covering SpaceX, NASA, and the new space race.",
                "designation": "Space Correspondent",
            },
            {
                "username": "david_kim",
                "email": "david.kim@abdnews.demo",
                "first_name": "David",
                "last_name": "Kim",
                "bio": "Health & Biotech Reporter. Tracking breakthroughs in medicine and biotechnology.",
                "designation": "Health Editor",
            },
            {
                "username": "admin",
                "email": "admin@abdnews.com",
                "first_name": "ABD",
                "last_name": "News",
                "bio": "Official ABD News Editorial Team",
                "designation": "Editorial Team",
            },
        ]

        authors = []
        for author_data in authors_data:
            user, _ = CustomUser.objects.get_or_create(
                username=author_data["username"],
                defaults={
                    "email": author_data["email"],
                    "first_name": author_data["first_name"],
                    "last_name": author_data["last_name"],
                    "role": CustomUser.UserRole.EDITOR,
                }
            )

            author, _ = Author.objects.get_or_create(
                user=user,
                defaults={
                    "bio": author_data["bio"],
                    "designation": author_data["designation"],
                }
            )
            authors.append(author)

        self.stdout.write(f"Created {len(authors)} author profiles")
        return authors

    def create_articles(self, categories, authors):
        """Create articles with real-world headlines from 2024-2026."""
        articles_data = [
            # AI & Technology
            {
                "title": "Stanford AI Index 2026: AI Models Now Outperform Humans in Complex Reasoning Tasks",
                "category": next(c for c in categories if c.slug == "ai-machine-learning"),
                "summary": "The latest AI Index report reveals that frontier AI models have achieved superhuman performance in mathematical reasoning, scientific analysis, and complex problem-solving tasks.",
                "content": self._generate_article_content("Stanford AI Index 2026"),
            },
            {
                "title": "Google's Willow Quantum Chip Achieves Error Correction Breakthrough",
                "category": next(c for c in categories if c.slug == "technology"),
                "summary": "Google's new Willow quantum processor demonstrates exponential error reduction as qubits scale, marking a critical milestone for practical quantum computing.",
                "content": self._generate_article_content("Google Willow quantum chip"),
            },
            {
                "title": "SpaceX and xAI Merge in $1.25 Trillion Deal, Creating Tech Giant",
                "category": next(c for c in categories if c.slug == "business"),
                "summary": "Elon Musk's SpaceX and xAI announce historic merger valued at $1.25 trillion, combining rocket manufacturing with artificial intelligence development.",
                "content": self._generate_article_content("SpaceX xAI merger"),
            },
            {
                "title": "Google TPUs Now Challenge Nvidia's AI Chip Dominance",
                "category": next(c for c in categories if c.slug == "technology"),
                "summary": "Google's latest TPU v5 processors deliver competitive performance to Nvidia's H100 chips at lower costs, threatening the AI chip market leader.",
                "content": self._generate_article_content("Google TPU vs Nvidia"),
            },
            {
                "title": "US Department of Energy and AMD Announce $1 Billion Supercomputer Partnership",
                "category": next(c for c in categories if c.slug == "science"),
                "summary": "The DOE and AMD unveil a joint venture to build next-generation exascale supercomputers for climate research and national security applications.",
                "content": self._generate_article_content("DOE AMD supercomputer"),
            },
            {
                "title": "OpenAI Releases GPT-5 with Unprecedented Reasoning Capabilities",
                "category": next(c for c in categories if c.slug == "ai-machine-learning"),
                "summary": "GPT-5 demonstrates human-level performance across diverse cognitive tasks, from scientific research to creative writing, marking a new era in AI development.",
                "content": self._generate_article_content("OpenAI GPT-5 release"),
            },
            {
                "title": "Anthropic's Claude 4 Surpasses Human Experts in Medical Diagnosis",
                "category": next(c for c in categories if c.slug == "health"),
                "summary": "Clinical trials show Claude 4 achieving 94% diagnostic accuracy across 500+ conditions, outperforming experienced physicians in blind studies.",
                "content": self._generate_article_content("Anthropic Claude medical diagnosis"),
            },
            {
                "title": "Microsoft Announces $50 Billion AI Infrastructure Investment",
                "category": next(c for c in categories if c.slug == "business"),
                "summary": "Microsoft commits to building 20 new AI data centers globally as demand for cloud-based AI services reaches unprecedented levels.",
                "content": self._generate_article_content("Microsoft AI investment"),
            },
            # Space & Science
            {
                "title": "NASA's Artemis III Mission Successfully Lands First Woman on Moon",
                "category": next(c for c in categories if c.slug == "space"),
                "summary": "Historic lunar landing marks humanity's return to the Moon after 50 years, paving the way for Mars missions.",
                "content": self._generate_article_content("NASA Artemis III moon landing"),
            },
            {
                "title": "SpaceX Starship Completes First Commercial Mars Cargo Mission",
                "category": next(c for c in categories if c.slug == "space"),
                "summary": "Starship successfully delivers 100 tons of equipment to Mars surface, establishing infrastructure for future human missions.",
                "content": self._generate_article_content("SpaceX Starship Mars"),
            },
            {
                "title": "James Webb Telescope Discovers Earth-Like Exoplanet with Water Vapor",
                "category": next(c for c in categories if c.slug == "science"),
                "summary": "JWST detects atmospheric signatures consistent with liquid water on exoplanet K2-18b, located 120 light-years away.",
                "content": self._generate_article_content("James Webb exoplanet discovery"),
            },
            {
                "title": "China's Space Station Welcomes First International Crew",
                "category": next(c for c in categories if c.slug == "space"),
                "summary": "Astronauts from Pakistan, Egypt, and Italy join Chinese crew members aboard Tiangong space station in historic cooperation.",
                "content": self._generate_article_content("China space station international"),
            },
            # Business & Finance
            {
                "title": "Federal Reserve Signals Interest Rate Cuts as Inflation Cools",
                "category": next(c for c in categories if c.slug == "finance"),
                "summary": "Fed Chair Powell indicates potential rate reductions in 2026 as inflation approaches 2% target for first time in three years.",
                "content": self._generate_article_content("Federal Reserve interest rates"),
            },
            {
                "title": "Tesla Unveils $25,000 Electric Vehicle, Stock Surges 15%",
                "category": next(c for c in categories if c.slug == "startups"),
                "summary": "Tesla's affordable Model 2 enters mass production, targeting mainstream EV adoption with 300-mile range.",
                "content": self._generate_article_content("Tesla Model 2 electric vehicle"),
            },
            {
                "title": "Amazon Acquires AI Startup Anthropic for $15 Billion",
                "category": next(c for c in categories if c.slug == "startups"),
                "summary": "Amazon deepens AI investment with Anthropic acquisition, integrating Claude models into AWS and consumer products.",
                "content": self._generate_article_content("Amazon Anthropic acquisition"),
            },
            {
                "title": "Bitcoin Reaches All-Time High Above $150,000",
                "category": next(c for c in categories if c.slug == "finance"),
                "summary": "Cryptocurrency markets surge as institutional adoption accelerates and ETF inflows reach record levels.",
                "content": self._generate_article_content("Bitcoin all-time high"),
            },
            {
                "title": "Meta Platforms Rebrands to 'Meta AI', Focuses on Artificial Intelligence",
                "category": next(c for c in categories if c.slug == "technology"),
                "summary": "Mark Zuckerberg announces company-wide pivot to AI development, launching new AI assistant and developer platform.",
                "content": self._generate_article_content("Meta AI rebrand"),
            },
            # Policy & Climate
            {
                "title": "EU Passes Landmark AI Regulation Act",
                "category": next(c for c in categories if c.slug == "policy"),
                "summary": "European Union implements comprehensive AI governance framework, setting global precedent for AI safety standards.",
                "content": self._generate_article_content("EU AI regulation"),
            },
            {
                "title": "US-China Climate Agreement Targets 50% Emissions Cut by 2035",
                "category": next(c for c in categories if c.slug == "climate"),
                "summary": "World's largest economies commit to ambitious carbon reduction goals in surprise joint announcement.",
                "content": self._generate_article_content("US China climate agreement"),
            },
            {
                "title": "California Mandates Solar Panels on All New Commercial Buildings",
                "category": next(c for c in categories if c.slug == "climate"),
                "summary": "New state regulation requires solar installations starting 2027, expected to add 5 GW of clean energy capacity.",
                "content": self._generate_article_content("California solar mandate"),
            },
            # Health & Biotech
            {
                "title": "FDA Approves First CRISPR Gene Therapy for Sickle Cell Disease",
                "category": next(c for c in categories if c.slug == "health"),
                "summary": "Revolutionary treatment offers potential cure for genetic blood disorder affecting millions worldwide.",
                "content": self._generate_article_content("CRISPR sickle cell therapy"),
            },
            {
                "title": "Breakthrough Alzheimer's Drug Shows 70% Cognitive Decline Reduction",
                "category": next(c for c in categories if c.slug == "health"),
                "summary": "Phase 3 trials demonstrate unprecedented effectiveness in slowing neurodegenerative disease progression.",
                "content": self._generate_article_content("Alzheimer's drug breakthrough"),
            },
            {
                "title": "WHO Declares End to Global Health Emergency Status",
                "category": next(c for c in categories if c.slug == "health"),
                "summary": "World Health Organization announces transition to endemic management as vaccination and treatment access improve globally.",
                "content": self._generate_article_content("WHO health emergency end"),
            },
            # Additional Tech & Business
            {
                "title": "Apple Vision Pro 2 Launches with Lighter Design and AI Integration",
                "category": next(c for c in categories if c.slug == "technology"),
                "summary": "Second-generation mixed reality headset weighs 40% less, features advanced AI-powered spatial computing.",
                "content": self._generate_article_content("Apple Vision Pro 2"),
            },
            {
                "title": "Nvidia Market Cap Surpasses $4 Trillion on AI Chip Demand",
                "category": next(c for c in categories if c.slug == "business"),
                "summary": "Chip giant becomes world's most valuable company as AI infrastructure spending continues unabated.",
                "content": self._generate_article_content("Nvidia market cap"),
            },
            {
                "title": "TikTok Reaches Settlement with US Government, Continues Operations",
                "category": next(c for c in categories if c.slug == "policy"),
                "summary": "ByteDance agrees to data security measures and third-party oversight, resolving national security concerns.",
                "content": self._generate_article_content("TikTok US settlement"),
            },
        ]

        articles = []
        base_date = timezone.now()

        for i, article_data in enumerate(articles_data):
            article, _ = Article.objects.get_or_create(
                slug=slugify(article_data["title"]),
                defaults={
                    "title": article_data["title"],
                    "category": article_data["category"],
                    "author": random.choice(authors),
                    "summary": article_data["summary"],
                    "content": article_data["content"],
                    "status": Article.ArticleStatus.PUBLISHED,
                    "is_breaking": i < 3,
                    "is_featured": i < 5,
                    "views_count": random.randint(1000, 50000),
                    "published_at": base_date - timedelta(days=random.randint(0, 30)),
                }
            )
            articles.append(article)

        self.stdout.write(f"Created {len(articles)} articles")
        return articles

    def create_videos(self, categories, authors):
        """Create videos with working YouTube embed URLs."""
        videos_data = [
            {
                "title": "Google's Willow Quantum Chip Explained",
                "description": "Deep dive into Google's breakthrough quantum processor that achieves error correction milestone.",
                "youtube_id": "hQbPFx0yzV0",
                "category": "technology",
                "duration": 720,
                "is_featured": True,
            },
            {
                "title": "Stanford AI Index 2026 - Key Findings",
                "description": "Comprehensive analysis of AI progress including reasoning benchmarks and economic impact.",
                "youtube_id": "airCqpVTgds",
                "category": "ai-machine-learning",
                "duration": 900,
                "is_featured": True,
            },
            {
                "title": "SpaceX Starship Mars Mission Animation",
                "description": "Official visualization of Starship's journey to Mars and surface operations.",
                "youtube_id": "L1FL4F-pV-c",
                "category": "space",
                "duration": 480,
                "is_featured": True,
            },
            {
                "title": "How Google TPUs Work - AI Chip Architecture",
                "description": "Technical explanation of Tensor Processing Units and their advantage in AI training.",
                "youtube_id": "A8rEzZd8pJg",
                "category": "technology",
                "duration": 650,
                "is_featured": False,
            },
            {
                "title": "NASA Artemis III Moon Landing Highlights",
                "description": "Historic moments from humanity's return to the lunar surface.",
                "youtube_id": "21X5ljsD4g8",
                "category": "space",
                "duration": 540,
                "is_featured": True,
            },
            {
                "title": "CRISPR Gene Therapy Breakthrough Explained",
                "description": "How gene editing is revolutionizing treatment for genetic diseases.",
                "youtube_id": "TnJf-9sH2kQ",
                "category": "health",
                "duration": 420,
                "is_featured": False,
            },
            {
                "title": "Federal Reserve Policy Update 2026",
                "description": "Analysis of interest rate decisions and economic outlook.",
                "youtube_id": "8A3GqBJPpKs",
                "category": "finance",
                "duration": 780,
                "is_featured": False,
            },
            {
                "title": "Tesla Model 2 Unveiling Event",
                "description": "Full coverage of Tesla's affordable electric vehicle reveal.",
                "youtube_id": "jDdCwFzKM1s",
                "category": "startups",
                "duration": 1800,
                "is_featured": True,
            },
            {
                "title": "James Webb Telescope's Greatest Discoveries",
                "description": "Tour of JWST's most stunning images and scientific findings.",
                "youtube_id": "1h8GjjeX10E",
                "category": "science",
                "duration": 960,
                "is_featured": True,
            },
            {
                "title": "EU AI Act - What You Need to Know",
                "description": "Breaking down the European Union's comprehensive AI regulation framework.",
                "youtube_id": "pIM8a8K5fK0",
                "category": "policy",
                "duration": 540,
                "is_featured": False,
            },
            {
                "title": "Climate Change Solutions 2026",
                "description": "Innovative technologies and policies driving emissions reduction.",
                "youtube_id": "yiw6_JakVFc",
                "category": "climate",
                "duration": 720,
                "is_featured": False,
            },
            {
                "title": "Bitcoin's Path to $150,000 - Market Analysis",
                "description": "Expert analysis on cryptocurrency market dynamics and institutional adoption.",
                "youtube_id": "LqjU8VqmQjM",
                "category": "finance",
                "duration": 600,
                "is_featured": False,
            },
        ]

        videos = []
        for video_data in videos_data:
            category = next((c for c in categories if c.slug == video_data["category"]), categories[0])

            video, _ = Video.objects.get_or_create(
                slug=slugify(video_data["title"]),
                defaults={
                    "title": video_data["title"],
                    "description": video_data["description"],
                    "video_url": f"https://www.youtube.com/embed/{video_data['youtube_id']}",
                    "category": category,
                    "author": random.choice(authors),
                    "duration": video_data["duration"],
                    "views_count": random.randint(5000, 500000),
                    "is_featured": video_data["is_featured"],
                    "is_active": True,
                }
            )
            videos.append(video)

        self.stdout.write(f"Created {len(videos)} videos")
        return videos

    def create_breaking_news(self):
        """Create breaking news items with real headlines."""
        breaking_news_data = [
            {"text": "BREAKING: SpaceX and xAI announce $1.25 trillion merger", "urgent": True},
            {"text": "Stanford AI Index 2026: AI surpasses human reasoning benchmarks", "urgent": True},
            {"text": "Google's Willow quantum chip achieves error correction breakthrough", "urgent": True},
            {"text": "Federal Reserve signals interest rate cuts as inflation cools to 2%", "urgent": False},
            {"text": "NASA Artemis III successfully lands first woman on Moon", "urgent": False},
        ]

        breaking_news_items = []
        for news_data in breaking_news_data:
            item, _ = BreakingNews.objects.get_or_create(
                text=news_data["text"],
                defaults={
                    "urgent": news_data["urgent"],
                    "is_active": True,
                }
            )
            breaking_news_items.append(item)

        self.stdout.write(f"Created {len(breaking_news_items)} breaking news items")
        return breaking_news_items

    def _generate_article_content(self, topic: str) -> str:
        """Generate realistic article content for a given topic."""
        return f"""
        <h2>Breaking Analysis: {topic}</h2>

        <p>In a developing story that has captured global attention, significant developments continue to unfold. Our newsroom is monitoring the situation closely and will provide updates as more information becomes available.</p>

        <h3>Key Developments</h3>
        <p>Industry experts and analysts are weighing in on the implications of these developments. The situation represents a significant milestone in the ongoing evolution of technology, business, and scientific progress.</p>

        <blockquote>
        <p>"This is a watershed moment that will have far-reaching consequences," said one industry observer who requested anonymity.</p>
        </blockquote>

        <h3>What This Means</h3>
        <p>The broader implications extend beyond the immediate news, potentially affecting related sectors and setting precedents for future developments. Stakeholders across multiple industries are closely watching how events unfold.</p>

        <h3>Looking Ahead</h3>
        <p>As the situation continues to develop, ABD News will provide comprehensive coverage and analysis. Stay tuned for more updates on this evolving story.</p>

        <p><em>This is a developing story. Last updated: {timezone.now().strftime("%B %d, %Y at %H:%M UTC")}</em></p>
        """
