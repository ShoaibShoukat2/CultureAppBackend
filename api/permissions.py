# permissions.py - Complete Custom Permissions
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed for any request.
    Write permissions are only allowed to the owner.
    """
    
    message = "You must be the owner to perform this action."
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        # Allow read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific object"""
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the object has a 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object is the user itself (CustomUser model)
        if hasattr(obj, 'username'):
            return obj == request.user
        
        # Check various owner fields
        owner_fields = ['artist', 'buyer', 'sender', 'reviewer', 'payer', 'owner']
        for field in owner_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if owner == request.user:
                    return True
        
        return False


class IsArtistOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow artists to create/edit certain objects.
    """
    
    message = "Only artists can perform this action."
    
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for authenticated artists
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'artist'
        )
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner artist
        if hasattr(obj, 'artist'):
            return obj.artist == request.user
        
        return request.user.user_type == 'artist'


class IsBuyerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow buyers to create/edit certain objects.
    """
    
    message = "Only buyers can perform this action."
    
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for authenticated buyers
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'buyer'
        )
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner buyer
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        
        return request.user.user_type == 'buyer'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow admin users to write.
    """
    
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin users
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type == 'admin' or request.user.is_staff or request.user.is_superuser)
        )


class IsArtistProfile(permissions.BasePermission):
    """
    Permission for artist profile operations.
    Only the artist can edit their own profile.
    """
    
    message = "You can only edit your own artist profile."
    
    def has_permission(self, request, view):
        # Allow read for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write requires authenticated artist
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'artist'
        )
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the profile owner
        return (
            request.user.is_authenticated and 
            obj.user == request.user and 
            request.user.user_type == 'artist'
        )


class IsBuyerProfile(permissions.BasePermission):
    """
    Permission for buyer profile operations.
    Only the buyer can edit their own profile.
    """
    
    message = "You can only edit your own buyer profile."
    
    def has_permission(self, request, view):
        # Allow read for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write requires authenticated buyer
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'buyer'
        )
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the profile owner
        return (
            request.user.is_authenticated and 
            obj.user == request.user and 
            request.user.user_type == 'buyer'
        )
        


class CanBidOnJob(permissions.BasePermission):
    """
    Permission to check if user can bid on a job.
    Only artists can bid, and they cannot bid on their own jobs.
    """
    
    message = "Only artists can bid on jobs."
    
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Only artists can create bids
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'artist'
        )
    
    def has_object_permission(self, request, view, obj):
        # Artists can only edit their own bids
        if hasattr(obj, 'artist'):
            return obj.artist == request.user
        return False


class CanReviewJob(permissions.BasePermission):
    """
    Permission to check if user can review a job.
    Only buyers who hired for the job can leave reviews.
    """
    
    message = "Only the buyer who hired the artist can leave a review."
    
    def has_permission(self, request, view):
        # Only authenticated buyers can review
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'buyer'
        )
    
    def has_object_permission(self, request, view, obj):
        # For review creation, check if user is the job buyer
        if hasattr(obj, 'buyer'):  # Job object
            return obj.buyer == request.user and obj.status == 'completed'
        
        # For existing reviews, check if user is the reviewer
        if hasattr(obj, 'reviewer'):  # Review object
            return obj.reviewer == request.user
        
        return False


class CanManageContract(permissions.BasePermission):
    """
    Permission for contract management.
    Both artist and buyer can view and sign.
    Only buyer can create/edit the contract.
    """
    
    message = "You don't have permission to manage this contract."
    
    def has_permission(self, request, view):
        # Contracts require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Both parties can view the contract
        if request.method in permissions.SAFE_METHODS:
            return (obj.artist == request.user or obj.buyer == request.user)
        
        # Both parties can sign the contract
        if view.action == 'sign':
            return (obj.artist == request.user or obj.buyer == request.user)
        
        # Only buyer can edit contract details
        return obj.buyer == request.user


class CanAccessMessages(permissions.BasePermission):
    """
    Permission for message access.
    Only sender and receiver can access messages.
    """
    
    message = "You can only access your own messages."
    
    def has_permission(self, request, view):
        # Messages require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only sender and receiver can access
        return (obj.sender == request.user or obj.receiver == request.user)


class CanAccessPayment(permissions.BasePermission):
    """
    Permission for payment access.
    Only payer and payee can access payment details.
    """
    
    message = "You can only access your own payments."
    
    def has_permission(self, request, view):
        # Payments require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only payer and payee can access
        return (
            obj.payer == request.user or 
            (obj.payee and obj.payee == request.user)
        )


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to check if user is verified.
    Can be used for sensitive operations.
    """
    
    message = "Your account must be verified to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_verified
        )


class CanHireArtist(permissions.BasePermission):
    """
    Permission to hire an artist for a job.
    Only the job buyer can hire.
    """
    
    message = "Only the job owner can hire an artist."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'buyer'
        )
    
    def has_object_permission(self, request, view, obj):
        # Only job buyer can hire
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        return False


class CanCompleteJob(permissions.BasePermission):
    """
    Permission to complete a job.
    Only the buyer can mark job as complete.
    """
    
    message = "Only the buyer can complete the job."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'buyer'
        )
    
    def has_object_permission(self, request, view, obj):
        # Only job buyer can complete
        if hasattr(obj, 'buyer'):
            return obj.buyer == request.user and obj.status == 'in_progress'
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for owner or admin access.
    Useful for moderation purposes.
    """
    
    message = "You must be the owner or an administrator."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.user_type == 'admin' or request.user.is_staff:
            return True
        
        # Check ownership
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        owner_fields = ['artist', 'buyer', 'sender', 'owner']
        for field in owner_fields:
            if hasattr(obj, field):
                if getattr(obj, field) == request.user:
                    return True
        
        return False