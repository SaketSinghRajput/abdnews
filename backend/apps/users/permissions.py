"""
Custom permission classes for subscription and role-based access control
"""
from rest_framework import permissions


class IsSubscribed(permissions.BasePermission):
    """
    Permission class to check if user has an active subscription
    """
    message = "You must have an active subscription to access this content."
    
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for browsing
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Admin bypasses subscription check
        if request.user.role == 'admin':
            return True
        
        # Check for active subscription
        return request.user.has_active_subscription


class IsSubscribedOrReadOnly(permissions.BasePermission):
    """
    Allow full article access only to subscribed users
    Non-subscribed users get limited preview
    """
    message = "Subscribe to read the full article."
    
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        # Anyone can see list/preview
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Full access only for subscribed users
        if request.user.is_authenticated:
            if request.user.role == 'admin':
                return True
            return request.user.has_active_subscription
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone, but editing only to admins
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow users to edit their own profile, or admins to edit any
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj == request.user


class IsStaffUser(permissions.BasePermission):
    """
    Only allow admin, editor, or journalist access
    """
    message = "You must be a staff member to access this resource."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'editor', 'journalist']
