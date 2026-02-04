#!/usr/bin/env python
"""
Demo Data Setup Script for NewsHub
Run this script on EC2 server to populate the database with sample content.
Usage: python scripts/setup_demo_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.articles.models import Article, Category
from apps.users.models import SubscriptionPlan, UserSubscription

User = get_user_model()

def create_categories():
    """Create demo categories"""
    print("Creating categories...")
    
    categories_data = [
        {'name': 'Politics', 'slug': 'politics', 'description': 'Latest political news and analysis', 'color': '#c8102e'},
        {'name': 'Technology', 'slug': 'technology', 'description': 'Tech innovations and digital trends', 'color': '#17417c'},
        {'name': 'Business', 'slug': 'business', 'description': 'Market insights and financial news', 'color': '#ffb703'},
        {'name': 'Entertainment', 'slug': 'entertainment', 'description': 'Movies, music, and celebrity news', 'color': '#e63946'},
        {'name': 'Sports', 'slug': 'sports', 'description': 'Sports updates and match coverage', 'color': '#2a9d8f'},
        {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness news', 'color': '#06a77d'},
        {'name': 'Science', 'slug': 'science', 'description': 'Scientific discoveries and research', 'color': '#457b9d'},
        {'name': 'Lifestyle', 'slug': 'lifestyle', 'description': 'Fashion, food, and living', 'color': '#f4a261'},
        {'name': 'Opinion', 'slug': 'opinion', 'description': 'Editorial opinions and analysis', 'color': '#8d99ae'},
        {'name': 'World', 'slug': 'world', 'description': 'International news and global events', 'color': '#2b2d42'},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"  ✓ Created category: {category.name}")
        else:
            print(f"  - Category already exists: {category.name}")
        created_categories.append(category)
    
    return created_categories


def create_subscription_plans():
    """Create subscription plans"""
    print("\nCreating subscription plans...")
    
    plans_data = [
        {
            'name': 'Free',
            'plan_type': 'free',
            'price': 0.00,
            'duration_days': 0,
            'description': 'Basic access to news articles with limited features',
            'includes_email_notifications': False,
            'includes_newsletter': False,
            'max_articles_per_month': 10,
        },
        {
            'name': 'Premium Monthly',
            'plan_type': 'monthly',
            'price': 9.99,
            'duration_days': 30,
            'description': 'Full access to all articles, videos, and premium content',
            'includes_email_notifications': True,
            'includes_newsletter': True,
            'max_articles_per_month': 0,  # Unlimited
        },
        {
            'name': 'Premium Yearly',
            'plan_type': 'yearly',
            'price': 99.99,
            'duration_days': 365,
            'description': 'Best value! Full access for a year with 2 months free',
            'includes_email_notifications': True,
            'includes_newsletter': True,
            'max_articles_per_month': 0,  # Unlimited
        }
    ]
    
    created_plans = []
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type=plan_data['plan_type'],
            defaults=plan_data
        )
        if created:
            print(f"  ✓ Created plan: {plan.name} - ${plan.price}")
        else:
            print(f"  - Plan already exists: {plan.name}")
        created_plans.append(plan)
    
    return created_plans


def create_demo_users():
    """Create demo users"""
    print("\nCreating demo users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@newshub.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'editor',
            'email': 'editor@newshub.com',
            'first_name': 'Chief',
            'last_name': 'Editor',
            'role': 'editor',
            'is_staff': True,
        },
        {
            'username': 'journalist1',
            'email': 'john.smith@newshub.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': 'journalist',
            'is_staff': True,
        },
        {
            'username': 'journalist2',
            'email': 'sarah.johnson@newshub.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'journalist',
            'is_staff': True,
        },
        {
            'username': 'subscriber1',
            'email': 'subscriber@example.com',
            'first_name': 'Premium',
            'last_name': 'Subscriber',
            'role': 'subscriber',
        }
    ]
    
    created_users = []
    default_password = 'Demo@123456'
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
            }
        )
        
        if created:
            user.set_password(default_password)
            user.save()
            print(f"  ✓ Created user: {user.username} (password: {default_password})")
        else:
            print(f"  - User already exists: {user.username}")
        
        created_users.append(user)
    
    return created_users


def create_demo_articles(categories, users):
    """Create demo articles"""
    print("\nCreating demo articles...")
    
    # Get journalist users
    journalists = [u for u in users if u.role == 'journalist']
    if not journalists:
        journalists = users[:2]  # Use first 2 users if no journalists
    
    articles_data = [
        {
            'title': 'Breaking: Global Markets Rally as Economic Indicators Show Strong Recovery',
            'slug': 'global-markets-rally-economic-recovery',
            'summary': 'Stock markets worldwide surge as key economic indicators point to robust recovery across major economies.',
            'content': '''Stock markets around the world experienced significant gains today as multiple economic indicators pointed to a stronger-than-expected recovery. The S&P 500 rose 2.3%, while European and Asian markets showed similar trends.

Key highlights:
- GDP growth exceeded forecasts in major economies
- Unemployment rates continue to decline
- Consumer confidence reaches five-year high
- Manufacturing output shows sustained improvement

Economists attribute the positive momentum to several factors, including coordinated fiscal policies, technological innovation, and improved supply chain management. However, some analysts caution that challenges remain, including inflation concerns and geopolitical uncertainties.

"This is an encouraging sign, but we need to remain vigilant," says Dr. Elizabeth Chen, Chief Economist at Global Finance Institute. "Sustainable growth requires continued policy support and structural reforms."

Investors are now closely watching upcoming central bank decisions and corporate earnings reports for further direction.''',
            'category': 'business',
            'is_featured': True,
            'is_breaking': True,
            'views_count': 15234,
        },
        {
            'title': 'Revolutionary AI System Achieves Breakthrough in Medical Diagnosis',
            'slug': 'ai-breakthrough-medical-diagnosis',
            'summary': 'New artificial intelligence system demonstrates 98% accuracy in early disease detection, promising to transform healthcare.',
            'content': '''Researchers at the Institute of Advanced Medical AI have unveiled a groundbreaking artificial intelligence system capable of detecting multiple diseases with unprecedented accuracy.

The system, named MediScan AI, analyzes medical imaging, patient history, and genetic data to identify early signs of conditions including cancer, cardiovascular disease, and neurological disorders. In clinical trials involving 50,000 patients across 20 countries, the system achieved 98.7% accuracy in disease detection.

Key features:
- Real-time analysis of medical scans
- Integration with electronic health records
- Predictive modeling for disease progression
- Personalized treatment recommendations

Dr. James Rodriguez, lead researcher on the project, explains: "This technology doesn't replace doctors; it empowers them with tools to make faster, more accurate diagnoses. Early detection can save lives and reduce treatment costs."

The system is expected to be deployed in major hospitals worldwide by next year, with plans to make it accessible to underserved communities through partnerships with global health organizations.''',
            'category': 'technology',
            'is_featured': True,
            'views_count': 12890,
        },
        {
            'title': 'Climate Summit Concludes with Historic Agreement on Carbon Emissions',
            'slug': 'climate-summit-historic-agreement',
            'summary': 'Nations commit to ambitious carbon reduction targets in landmark environmental accord.',
            'content': '''World leaders concluded the Global Climate Summit today with a historic agreement committing 195 nations to aggressive carbon emission reduction targets.

The accord, dubbed the "Green Future Pact," includes:
- 60% reduction in carbon emissions by 2035
- $2 trillion global fund for renewable energy projects
- Technology sharing for developing nations
- Mandatory climate reporting standards
- Protection of critical ecosystems

UN Secretary-General praised the agreement as "a turning point in humanity's response to climate change." Environmental groups, while welcoming the commitment, emphasized the need for immediate action and accountability.

The agreement includes enforcement mechanisms and regular review cycles to ensure nations meet their commitments. Major economies pledged to accelerate the transition to clean energy and phase out fossil fuel subsidies.

"This is just the beginning," stated environmental activist Maya Patel. "Now comes the hard work of implementation and holding governments accountable."''',
            'category': 'world',
            'is_featured': False,
            'views_count': 9876,
        },
        {
            'title': 'Championship Finals: Underdogs Secure Victory in Thrilling Overtime',
            'slug': 'championship-finals-overtime-victory',
            'summary': 'Historic comeback in the final minutes leads to championship win for the underdogs.',
            'content': '''In what many are calling the greatest championship game in decades, the underdog Thunderbolts secured a stunning victory against the defending champions in overtime.

Down by 15 points with just 8 minutes remaining, the Thunderbolts mounted an incredible comeback, tying the game with seconds left in regulation. The overtime period saw exceptional performances from both teams before the Thunderbolts sealed the victory with a dramatic final play.

Match highlights:
- MVP: Alex Martinez with 42 points, 12 rebounds
- Historic comeback from 15-point deficit
- 5 lead changes in the final quarter
- Record-breaking attendance of 75,000 fans

"This team never gave up," said head coach Michael Thompson. "We believed in ourselves when nobody else did. This victory is for every player, every fan, and everyone who supported us throughout this journey."

The championship marks the team's first title in 30 years and caps off a remarkable season that saw them overcome injuries and adversity to reach the pinnacle of their sport.''',
            'category': 'sports',
            'is_featured': False,
            'views_count': 8765,
        },
        {
            'title': 'New Study Reveals Benefits of Mediterranean Diet on Heart Health',
            'slug': 'mediterranean-diet-heart-health-study',
            'summary': 'Comprehensive research confirms significant cardiovascular benefits of Mediterranean eating patterns.',
            'content': '''A landmark study involving 100,000 participants over 15 years has provided compelling evidence of the Mediterranean diet's profound impact on heart health.

The research, published in the Journal of Cardiovascular Medicine, found that individuals following a Mediterranean diet experienced:
- 35% reduction in heart disease risk
- 30% lower rates of stroke
- Improved cholesterol levels
- Better blood pressure control
- Reduced inflammation markers

The Mediterranean diet emphasizes:
- Olive oil as the primary fat source
- Abundant fruits and vegetables
- Whole grains and legumes
- Moderate fish and poultry consumption
- Limited red meat intake
- Moderate wine consumption with meals

Dr. Maria Rossi, lead researcher, notes: "The benefits extend beyond heart health. Participants also showed improvements in cognitive function, weight management, and overall quality of life."

Nutritionists recommend gradual adoption of Mediterranean eating patterns, starting with simple changes like replacing butter with olive oil and increasing vegetable intake. The study provides strong evidence for dietary interventions in preventing cardiovascular disease.''',
            'category': 'health',
            'is_featured': False,
            'views_count': 7654,
        },
        {
            'title': 'Space Agency Announces Plans for First Permanent Moon Base',
            'slug': 'moon-base-permanent-settlement-plans',
            'summary': 'Ambitious project aims to establish self-sustaining lunar colony by 2035.',
            'content': '''The Global Space Agency unveiled detailed plans today for humanity's first permanent settlement on the Moon, marking a new era in space exploration.

The Lunar Gateway Project will establish a self-sustaining base capable of housing up to 100 people continuously. The facility will serve as a launching point for deep space missions and a hub for scientific research.

Project timeline:
- 2027: Initial habitat modules deployment
- 2029: Power and life support systems activation
- 2031: First crew rotation begins
- 2035: Full operational capacity

The base will feature:
- Advanced 3D-printed structures using lunar regolith
- Solar and nuclear power generation
- Water extraction from lunar ice
- Hydroponic food production systems
- Scientific laboratories
- Launch facilities for Mars missions

"This represents humanity's commitment to becoming a multi-planetary species," stated Space Agency Director Chen Wei. "The Moon base will demonstrate technologies essential for future Mars colonization."

International partnerships and private sector involvement will fund the $500 billion project. Multiple countries and space companies have committed resources and expertise to this historic endeavor.''',
            'category': 'science',
            'is_featured': True,
            'views_count': 11234,
        },
        {
            'title': 'Fashion Week Showcases Sustainable Future of Clothing Industry',
            'slug': 'fashion-week-sustainable-clothing-future',
            'summary': 'Major designers embrace eco-friendly materials and ethical production in groundbreaking collections.',
            'content': '''This year's Fashion Week marked a turning point for the industry as sustainability took center stage, with leading designers presenting collections made entirely from eco-friendly materials.

Highlights include:
- Biodegradable fabrics from mushroom and algae
- Clothes made from recycled ocean plastics
- Zero-waste production techniques
- Transparent supply chains
- Fair trade labor practices

Designer Elena Fontaine explained: "Fashion can no longer ignore its environmental impact. We're proving that style and sustainability can coexist beautifully."

The shift reflects growing consumer demand for ethical fashion. Studies show 73% of millennials willing to pay more for sustainable products. Major brands are responding with circular economy initiatives, rental programs, and take-back schemes.

Industry analysts predict sustainable fashion will dominate the market within a decade. Technology innovations like lab-grown leather and digital design tools are accelerating the transition.

"This isn't just a trend; it's the future of fashion," notes sustainability consultant Mark Davidson. "Brands that don't adapt will be left behind."''',
            'category': 'lifestyle',
            'is_featured': False,
            'views_count': 6543,
        },
        {
            'title': 'Tech Giants Face Increased Scrutiny Over Data Privacy Practices',
            'slug': 'tech-giants-data-privacy-scrutiny',
            'summary': 'Regulators worldwide intensify investigations into user data collection and usage.',
            'content': '''Major technology companies are facing mounting pressure from regulators worldwide over their data collection practices and user privacy protections.

Recent developments:
- EU fines totaling $5 billion for GDPR violations
- US Congressional hearings on data monetization
- New privacy laws enacted in 15 countries
- Class-action lawsuits from consumer groups
- Demands for greater transparency

The investigations focus on:
- Unauthorized data sharing with third parties
- Inadequate user consent mechanisms
- Hidden tracking technologies
- Sale of personal information
- Security breaches and data leaks

Consumer advocacy groups are calling for stricter regulations and heavier penalties. "Users deserve control over their personal information," states digital rights activist Jennifer Park. "Current practices are unacceptable."

Tech companies defend their practices but acknowledge the need for reform. Several have announced enhanced privacy features, data deletion options, and clearer terms of service.

Legal experts predict significant regulatory changes ahead, potentially reshaping how technology companies operate and monetize user data.''',
            'category': 'technology',
            'is_featured': False,
            'views_count': 5678,
        },
        {
            'title': 'Political Debate Highlights Deep Divisions on Economic Policy',
            'slug': 'political-debate-economic-policy-divisions',
            'summary': 'Candidates present contrasting visions for economic future in heated debate.',
            'content': '''Last night's political debate showcased stark differences between candidates on key economic issues, reflecting broader societal divisions.

Major points of contention:
- Tax policy and wealth distribution
- Healthcare funding and coverage
- Infrastructure investment priorities
- Climate change economic impact
- Trade agreements and tariffs

Candidate Adams advocated for:
- Progressive tax system with higher rates for wealthy
- Universal healthcare program
- Green energy investment
- Strengthened social safety net

Candidate Bennett proposed:
- Tax cuts to stimulate business growth
- Market-based healthcare solutions
- Reduced government spending
- Traditional energy sector support

Political analysts note the debate reflected growing polarization on economic philosophy. "We're seeing fundamentally different visions for the country's economic future," observes political scientist Dr. Robert Martinez.

Polls show voters deeply divided, with demographics playing a significant role in policy preferences. Economic issues are expected to dominate the campaign as election day approaches.

Both candidates emphasized job creation and economic growth but offered markedly different approaches to achieving these goals.''',
            'category': 'politics',
            'is_featured': False,
            'views_count': 4987,
        },
        {
            'title': 'Blockbuster Film Breaks Opening Weekend Records Worldwide',
            'slug': 'blockbuster-film-opening-weekend-records',
            'summary': 'Epic sci-fi adventure exceeds expectations with $450 million global debut.',
            'content': '''The highly anticipated sci-fi epic "Stellar Horizons" shattered box office records this weekend, earning $450 million globally in its opening three days.

Box office breakdown:
- North America: $180 million
- China: $120 million
- International markets: $150 million
- IMAX screens: $60 million

The film's success is attributed to:
- Stunning visual effects and cinematography
- Compelling story and character development
- Strong performances from ensemble cast
- Positive critical reception (94% on review aggregators)
- Strategic global release timing

Director Sophia Chen commented: "This film is a love letter to science fiction fans. The support has been overwhelming and humbling."

Industry analysts project the film could reach $2 billion worldwide, potentially joining the elite club of highest-grossing films. The success is particularly significant as it marks a strong recovery for theatrical releases following years of streaming dominance.

Sequel announcements are expected soon, with the studio already developing an expanded universe of related content. The film has also sparked renewed interest in practical effects and large-scale sci-fi productions.

"Stellar Horizons proves that original, well-crafted stories can still dominate the box office," notes entertainment analyst Kevin Wu.''',
            'category': 'entertainment',
            'is_featured': True,
            'views_count': 13456,
        }
    ]
    
    created_articles = []
    for i, article_data in enumerate(articles_data):
        # Find category
        category = next((c for c in categories if c.slug == article_data['category']), categories[0])
        
        # Random author from journalists
        author = random.choice(journalists)
        
        # Published date between 7 days ago and now
        published_at = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        
        # Create article
        article, created = Article.objects.get_or_create(
            slug=article_data['slug'],
            defaults={
                'title': article_data['title'],
                'summary': article_data['summary'],
                'content': article_data['content'],
                'category': category,
                'author': author,
                'is_featured': article_data.get('is_featured', False),
                'is_breaking': article_data.get('is_breaking', False),
                'views_count': article_data.get('views_count', 0),
                'status': 'published',
                'published_at': published_at,
            }
        )
        
        if created:
            print(f"  ✓ Created article: {article.title[:60]}...")
        else:
            print(f"  - Article already exists: {article.title[:60]}...")
        
        created_articles.append(article)
    
    return created_articles


def main():
    """Main setup function"""
    print("=" * 70)
    print("NewsHub Demo Data Setup")
    print("=" * 70)
    
    try:
        # Create categories
        categories = create_categories()
        
        # Create subscription plans
        plans = create_subscription_plans()
        
        # Create demo users
        users = create_demo_users()
        
        # Create demo articles
        articles = create_demo_articles(categories, users)
        
        print("\n" + "=" * 70)
        print("✓ Demo data setup completed successfully!")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  - Categories: {len(categories)}")
        print(f"  - Subscription Plans: {len(plans)}")
        print(f"  - Users: {len(users)}")
        print(f"  - Articles: {len(articles)}")
        print(f"\nDefault password for all users: Demo@123456")
        print(f"Admin user: admin / Demo@123456")
        print(f"\nYou can now access:")
        print(f"  - Admin panel: http://your-domain.com/admin/")
        print(f"  - Frontend: http://your-domain.com/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
