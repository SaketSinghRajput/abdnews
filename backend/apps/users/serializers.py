from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Author, SubscriptionPlan, UserSubscription


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading user information"""
    has_active_subscription = serializers.ReadOnlyField()
    subscription_plan = serializers.SerializerMethodField()
    subscription_start_date = serializers.SerializerMethodField()
    subscription_end_date = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'date_joined', 'is_subscribed',
            'subscription_start', 'subscription_end', 'has_active_subscription',
            'email_notifications', 'newsletter_subscription', 'is_active',
            'subscription_plan', 'subscription_start_date', 'subscription_end_date'
        ]
        read_only_fields = ['id', 'date_joined', 'is_subscribed', 'subscription_start', 'subscription_end', 'is_active']
    
    def get_subscription_plan(self, obj):
        """Get the current subscription plan name"""
        try:
            from .models import UserSubscription
            sub = UserSubscription.objects.filter(user=obj, status='active').order_by('-start_date').first()
            if sub:
                return sub.plan.name
        except:
            pass
        return None
    
    def get_subscription_start_date(self, obj):
        """Get subscription start date"""
        try:
            from .models import UserSubscription
            sub = UserSubscription.objects.filter(user=obj, status='active').order_by('-start_date').first()
            if sub:
                return sub.start_date.isoformat()
        except:
            pass
        return None
    
    def get_subscription_end_date(self, obj):
        """Get subscription end date"""
        try:
            from .models import UserSubscription
            sub = UserSubscription.objects.filter(user=obj, status='active').order_by('-start_date').first()
            if sub:
                return sub.end_date.isoformat()
        except:
            pass
        return None


class SignupSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number'
        ]
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        """Create user with hashed password and subscriber role"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data, role='subscriber')
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate with username/email
            user = authenticate(username=username, password=password)
            
            if not user:
                # Try with email
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError("Invalid username/email or password.")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'status', 
            'start_date', 'end_date', 'auto_renew', 'is_active',
            'payment_reference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for author profiles"""
    
    full_name = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'user', 'full_name', 'designation', 'bio',
            'profile_image', 'social_links', 'is_featured',
            'article_count', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'article_count', 'created_at']
    
    def get_full_name(self, obj):
        """Get author's full name"""
        return obj.get_full_name()
    
    def get_social_links(self, obj):
        """Get social media links"""
        return obj.get_social_links()


class AuthorDetailSerializer(AuthorSerializer):
    """Extended serializer with full user details"""
    
    user = UserSerializer(read_only=True)
    
    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields
        read_only_fields = AuthorSerializer.Meta.read_only_fields
