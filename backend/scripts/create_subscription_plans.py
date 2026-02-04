"""
Script to create sample subscription plans for NewsHub
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import SubscriptionPlan

# Clear existing plans
SubscriptionPlan.objects.all().delete()

# Create subscription plans
plans = [
    {
        'name': 'Free',
        'plan_type': 'free',
        'price': 0.00,
        'duration_days': 365,  # 1 year free access
        'description': 'Free access to basic news articles',
        'features': [
            'Access to basic articles',
            'Limited articles per month (10 articles)',
            'Email newsletter (weekly)',
        ],
        'includes_email_notifications': True,
        'includes_newsletter': True,
        'is_active': True,
    },
    {
        'name': 'Premium Monthly',
        'plan_type': 'monthly',
        'price': 9.99,
        'duration_days': 30,
        'description': 'Full access to all premium articles and exclusive content',
        'features': [
            'Unlimited article access',
            'Ad-free reading experience',
            'Mobile app access',
            'Daily email newsletter',
            'Breaking news alerts',
            'Exclusive editorials',
            'Priority customer support',
        ],
        'includes_email_notifications': True,
        'includes_newsletter': True,
        'is_active': True,
    },
]

for plan_data in plans:
    plan = SubscriptionPlan.objects.create(**plan_data)
    print(f'✅ Created: {plan.name} - ${plan.price} for {plan.duration_days} days')

print(f'\n🎉 Successfully created {SubscriptionPlan.objects.count()} subscription plans!')
