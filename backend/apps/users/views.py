"""
User and author API views for NewsHub.

Provides ViewSets for user management, author profiles, and
token-based authentication endpoints.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import logout
from .models import CustomUser, Author
from .serializers import (
    UserSerializer,
    SignupSerializer,
    AuthorSerializer,
    AuthorDetailSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management (admin only)"""
    
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        """Use registration serializer for create action"""
        if self.action == 'create':
            return UserRegistrationSerializer
        return self.serializer_class
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for author profiles (read-only for non-staff)"""
    
    queryset = Author.objects.select_related('user')
    serializer_class = AuthorSerializer
    
    def get_permissions(self):
        """Allow read for all, write only for admin"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return AuthorDetailSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """Filter featured authors if requested"""
        queryset = Author.objects.select_related('user')
        is_featured = self.request.query_params.get('is_featured', None)
        if is_featured is not None:
            is_featured = is_featured.lower() == 'true'
            queryset = queryset.filter(is_featured=is_featured)
        return queryset
    
    def perform_create(self, serializer):
        """Assign current user when creating author profile"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Prevent changing the user field on update"""
        # Save without allowing user field modification
        serializer.save()
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.AllowAny]
    )
    def featured(self, request):
        """Get featured authors only"""
        featured_authors = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_authors, many=True)
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    """Custom token authentication endpoint with user details"""
    
    def post(self, request, *args, **kwargs):
        """Validate credentials and return auth token with user metadata."""
        serializer = self.serializer_class(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })


class LogoutView(APIView):
    """Logout endpoint for token-based and session authentication"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Delete user token and logout"""
        # Delete token if exists
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        # Logout session
        logout(request)
        
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
