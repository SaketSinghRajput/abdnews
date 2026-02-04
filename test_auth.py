#!/usr/bin/env python
"""
Quick test script to verify authentication flow works
"""
import os
import sys
import django

# Add backend directory to path
sys.path.insert(0, 'f:\\Projects\\newsblog\\newshub\\backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import CustomUser, SubscriptionPlan

# Test 1: Check if subscription plans exist
print("=" * 60)
print("TEST 1: Checking Subscription Plans")
print("=" * 60)
plans = SubscriptionPlan.objects.all()
if plans.count() == 0:
    print("❌ No subscription plans found!")
    print("Creating subscription plans...")
    
    # Create Free plan
    free_plan = SubscriptionPlan.objects.create(
        name='Free Plan',
        plan_type='FREE',
        price=0,
        duration_days=0,  # Unlimited
        description='Free access with basic features',
        includes_email_notifications=False,
        includes_newsletter=False,
        is_active=True
    )
    print(f"✅ Created Free Plan: {free_plan}")
    
    # Create Premium plan
    premium_plan = SubscriptionPlan.objects.create(
        name='Premium Monthly',
        plan_type='PREMIUM',
        price=9.99,
        duration_days=30,
        description='Unlimited access to all content',
        includes_email_notifications=True,
        includes_newsletter=True,
        is_active=True
    )
    print(f"✅ Created Premium Plan: {premium_plan}")
else:
    print(f"✅ Found {plans.count()} subscription plans:")
    for plan in plans:
        print(f"   - {plan.name} (${plan.price})")

# Test 2: Check if test user exists, create if not
print("\n" + "=" * 60)
print("TEST 2: Creating Test User")
print("=" * 60)
test_user, created = CustomUser.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'subscriber',
        'is_active': True
    }
)

if created:
    test_user.set_password('testpass123')
    test_user.save()
    print(f"✅ Created test user: {test_user.username}")
else:
    print(f"✅ Test user already exists: {test_user.username}")

print(f"   Email: {test_user.email}")
print(f"   Role: {test_user.role}")

# Test 3: Verify password works
print("\n" + "=" * 60)
print("TEST 3: Testing Authentication")
print("=" * 60)
from django.contrib.auth import authenticate

user = authenticate(username='testuser', password='testpass123')
if user is not None:
    print(f"✅ Authentication successful: {user.username}")
else:
    print("❌ Authentication failed")

# Test 4: Show API endpoints
print("\n" + "=" * 60)
print("TEST 4: Available API Endpoints")
print("=" * 60)
endpoints = [
    "POST /api/users/auth/signup/ - User registration",
    "POST /api/users/auth/login/ - User login",
    "GET /api/users/auth/profile/ - Get user profile",
    "PUT /api/users/auth/profile/ - Update user profile",
    "POST /api/users/auth/logout/ - User logout",
    "POST /api/users/auth/token/refresh/ - Refresh token",
    "POST /api/users/change-password/ - Change password",
    "GET /api/users/subscription-plans/ - List subscription plans",
    "POST /api/users/subscribe/ - Subscribe to a plan"
]

for endpoint in endpoints:
    print(f"   {endpoint}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\nYou can now test the frontend at: http://127.0.0.1:8000/pages/login.html")
print("Test credentials:")
print("   Username: testuser")
print("   Password: testpass123")
