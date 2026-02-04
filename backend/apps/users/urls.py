from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, AuthorViewSet, CustomAuthToken, LogoutView
from . import auth_views

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT Authentication endpoints
    path('auth/signup/', auth_views.SignupView.as_view(), name='signup'),
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', auth_views.ProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', auth_views.ChangePasswordView.as_view(), name='change-password'),
    
    # Subscription endpoints
    path('subscription-plans/', auth_views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscriptions/', auth_views.UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('subscribe/', auth_views.SubscribeView.as_view(), name='subscribe'),
    
    # Legacy token authentication
    path('auth/token-login/', CustomAuthToken.as_view(), name='auth-login'),
    path('auth/token-logout/', LogoutView.as_view(), name='auth-logout'),
    
    # Session authentication (DRF browsable API)
    path('auth/', include('rest_framework.urls')),
]
