"""
Email utility functions for NewsHub
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def get_site_url():
    """Get the site URL"""
    # Return configured site URL or default
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


def send_welcome_email(user):
    """
    Send welcome email to new user
    """
    if not user.email_notifications:
        return False
    
    context = {
        'user_name': user.get_full_name() or user.username,
        'site_url': get_site_url(),
    }
    
    subject = 'Welcome to NewsHub!'
    html_message = render_to_string('emails/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False


def send_subscription_activated_email(user, subscription):
    """
    Send subscription activation email to user
    """
    if not user.email_notifications:
        return False
    
    plan = subscription.plan
    context = {
        'user_name': user.get_full_name() or user.username,
        'plan_name': plan.name if plan else 'Unknown Plan',
        'start_date': subscription.start_date.strftime('%B %d, %Y'),
        'end_date': subscription.end_date.strftime('%B %d, %Y'),
        'features': plan.features if plan and plan.features else [],
        'site_url': get_site_url(),
    }
    
    subject = f'Your {context["plan_name"]} Subscription is Active!'
    html_message = render_to_string('emails/subscription_activated.html', context)
    plain_message = render_to_string('emails/subscription_activated.txt', context)
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send subscription email: {e}")
        return False


def send_subscription_expiry_reminder(user, subscription, days_left):
    """
    Send subscription expiry reminder email
    """
    if not user.email_notifications:
        return False
    
    plan = subscription.plan
    context = {
        'user_name': user.get_full_name() or user.username,
        'plan_name': plan.name if plan else 'Unknown Plan',
        'days_left': days_left,
        'end_date': subscription.end_date.strftime('%B %d, %Y'),
        'site_url': get_site_url(),
    }
    
    subject = f'Your {context["plan_name"]} Subscription Expires in {days_left} Days'
    
    # Create a simple HTML template
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Subscription Expiry Reminder</h2>
        <p>Hi {context['user_name']},</p>
        <p>Your <strong>{context['plan_name']}</strong> subscription will expire in <strong>{days_left} days</strong> on {context['end_date']}.</p>
        <p>Renew your subscription to continue enjoying premium content.</p>
        <p><a href="{context['site_url']}/profile">Manage Subscription</a></p>
        <p>Best regards,<br>The NewsHub Team</p>
    </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send expiry reminder: {e}")
        return False


def send_newsletter(user, subject, content):
    """
    Send newsletter email to user
    """
    if not user.newsletter_subscription:
        return False
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(content, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send newsletter: {e}")
        return False
