from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Author, SubscriptionPlan, UserSubscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_subscribed', 'subscription_end', 'is_active']
    list_filter = ['role', 'is_subscribed', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Subscription', {
            'fields': ('role', 'phone_number', 'is_subscribed', 'subscription_start', 'subscription_end')
        }),
    )
    
    actions = ['activate_subscription', 'deactivate_subscription']
    
    def activate_subscription(self, request, queryset):
        """Activate 30-day subscription for selected users"""
        for user in queryset:
            user.activate_subscription(days=30)
        self.message_user(request, f"{queryset.count()} user(s) subscription activated for 30 days")
    activate_subscription.short_description = "Activate 30-day subscription"
    
    def deactivate_subscription(self, request, queryset):
        """Deactivate subscription for selected users"""
        for user in queryset:
            user.deactivate_subscription()
        self.message_user(request, f"{queryset.count()} user(s) subscription deactivated")
    deactivate_subscription.short_description = "Deactivate subscription"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin interface for Author"""
    list_display = ['get_full_name', 'designation', 'is_featured', 'article_count', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'designation']
    readonly_fields = ['article_count', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'designation', 'bio', 'is_featured')
        }),
        ('Media', {
            'fields': ('profile_image',)
        }),
        ('Social Links', {
            'fields': ('twitter_url', 'linkedin_url', 'facebook_url', 'website_url')
        }),
        ('Statistics', {
            'fields': ('article_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin interface for SubscriptionPlan"""
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'plan_type', 'price', 'duration_days', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for UserSubscription"""
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'is_active', 'auto_renew']
    list_filter = ['status', 'auto_renew', 'created_at']
    search_fields = ['user__username', 'user__email', 'payment_reference']
    readonly_fields = ['created_at', 'updated_at', 'is_active']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'auto_renew')
        }),
        ('Payment', {
            'fields': ('payment_reference',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_subscriptions', 'cancel_subscriptions', 'renew_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions"""
        for subscription in queryset:
            subscription.activate()
        self.message_user(request, f"{queryset.count()} subscription(s) activated")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def cancel_subscriptions(self, request, queryset):
        """Cancel selected subscriptions"""
        for subscription in queryset:
            subscription.cancel()
        self.message_user(request, f"{queryset.count()} subscription(s) cancelled")
    cancel_subscriptions.short_description = "Cancel selected subscriptions"
    
    def renew_subscriptions(self, request, queryset):
        """Renew selected subscriptions"""
        for subscription in queryset:
            subscription.renew()
        self.message_user(request, f"{queryset.count()} subscription(s) renewed")
    renew_subscriptions.short_description = "Renew selected subscriptions"
