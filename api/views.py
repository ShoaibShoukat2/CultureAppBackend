# views.py
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
import os
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsArtistOrReadOnly, IsBuyerOrReadOnly
from api.notifications.utils import send_notification_email, send_contract_notification_email


# Payment Views
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY



# Custom Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint with 2FA support"""
    from .two_factor_serializers import LoginWith2FASerializer
    from .two_factor_utils import create_2fa_session
    
    serializer = LoginWith2FASerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if user has 2FA enabled
        if user.two_factor_enabled:
            # Create 2FA session
            session = create_2fa_session(user)
            return Response({
                'requires_2fa': True,
                'session_token': session.session_token,
                'message': 'Please provide 2FA code'
            }, status=status.HTTP_200_OK)
        else:
            # Normal login without 2FA
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)


# 2FA Views
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa(request):
    """Verify 2FA code and complete login"""
    from .two_factor_serializers import Verify2FASerializer
    from .two_factor_utils import verify_2fa_session, verify_totp_code, use_backup_code
    
    serializer = Verify2FASerializer(data=request.data)
    if serializer.is_valid():
        session_token = serializer.validated_data['session_token']
        totp_code = serializer.validated_data.get('totp_code')
        backup_code = serializer.validated_data.get('backup_code')
        
        # Verify session
        session = verify_2fa_session(session_token)
        if not session:
            return Response({
                'error': 'Invalid or expired session'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = session.user
        
        # Verify 2FA code
        if totp_code:
            if not verify_totp_code(user.two_factor_secret, totp_code):
                return Response({
                    'error': 'Invalid TOTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
        elif backup_code:
            if not use_backup_code(user, backup_code):
                return Response({
                    'error': 'Invalid backup code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark session as used
        session.is_used = True
        session.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """Setup 2FA for user"""
    from .two_factor_utils import generate_secret_key, generate_qr_code
    from datetime import timedelta
    from .models import TwoFactorSetupSession
    
    user = request.user
    
    if user.two_factor_enabled:
        return Response({
            'error': '2FA is already enabled'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if there's already a valid setup session
    try:
        existing_session = TwoFactorSetupSession.objects.get(user=user)
        
        # If session is not expired, reuse it
        if not existing_session.is_expired():
            secret_key = existing_session.secret_key
            qr_code = generate_qr_code(user, secret_key)
            
            return Response({
                'secret_key': secret_key,
                'qr_code': qr_code,
                'message': 'Existing setup session found. Use the same QR code.',
                'expires_in_minutes': int((existing_session.expires_at - timezone.now()).total_seconds() / 60)
            }, status=status.HTTP_200_OK)
        else:
            # Session expired, delete it
            existing_session.delete()
            
    except TwoFactorSetupSession.DoesNotExist:
        # No existing session, continue with new setup
        pass
    
    # Generate new secret key
    secret_key = generate_secret_key()
    
    # Generate QR code
    qr_code = generate_qr_code(user, secret_key)
    
    # Create new setup session (expires in 30 minutes)
    setup_session = TwoFactorSetupSession.objects.create(
        user=user,
        secret_key=secret_key,
        expires_at=timezone.now() + timedelta(minutes=30)
    )
    
    return Response({
        'secret_key': secret_key,
        'qr_code': qr_code,
        'message': 'Scan QR code with your authenticator app',
        'expires_in_minutes': 30
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA after verification"""
    from .two_factor_serializers import Enable2FASerializer
    from .two_factor_utils import verify_totp_code, generate_backup_codes
    from .models import TwoFactorSetupSession
    
    serializer = Enable2FASerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        totp_code = serializer.validated_data['totp_code']
        
        # Get temporary secret from database
        try:
            setup_session = TwoFactorSetupSession.objects.get(user=user)
            
            # Check if session expired
            if setup_session.is_expired():
                setup_session.delete()
                return Response({
                    'error': 'Setup session expired. Please start setup again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            secret_key = setup_session.secret_key
            
        except TwoFactorSetupSession.DoesNotExist:
            return Response({
                'error': 'No 2FA setup session found. Please start setup again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify TOTP code
        if not verify_totp_code(secret_key, totp_code):
            return Response({
                'error': 'Invalid TOTP code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Enable 2FA
        user.two_factor_enabled = True
        user.two_factor_secret = secret_key
        user.backup_codes = generate_backup_codes()
        user.save()
        
        # Clear setup session
        setup_session.delete()
        
        return Response({
            'message': '2FA enabled successfully',
            'backup_codes': user.backup_codes
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable 2FA"""
    from .two_factor_serializers import Disable2FASerializer
    
    serializer = Disable2FASerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        
        # Disable 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.backup_codes = []
        user.save()
        
        return Response({
            'message': '2FA disabled successfully'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """Get 2FA status for user"""
    user = request.user
    return Response({
        'two_factor_enabled': user.two_factor_enabled,
        'backup_codes_count': len(user.backup_codes) if user.backup_codes else 0
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_backup_codes(request):
    """Regenerate backup codes"""
    from .two_factor_utils import generate_backup_codes
    
    user = request.user
    
    if not user.two_factor_enabled:
        return Response({
            'error': '2FA is not enabled'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate new backup codes
    user.backup_codes = generate_backup_codes()
    user.save()
    
    return Response({
        'backup_codes': user.backup_codes,
        'message': 'Backup codes regenerated successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_disable_2fa(request):
    """Force disable 2FA with password only (for testing/emergency)"""
    password = request.data.get('password')
    
    if not password:
        return Response({
            'error': 'Password is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Verify password
    if not user.check_password(password):
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Force disable 2FA
    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.backup_codes = []
    user.save()
    
    return Response({
        'message': '2FA force disabled successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_2fa_setup(request):
    """Reset 2FA setup session (generate new QR code)"""
    from .models import TwoFactorSetupSession
    
    user = request.user
    
    if user.two_factor_enabled:
        return Response({
            'error': '2FA is already enabled. Disable it first to reset setup.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete existing setup session
    TwoFactorSetupSession.objects.filter(user=user).delete()
    
    return Response({
        'message': 'Setup session reset. Call /setup/ again to get new QR code.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_disable_requirements(request):
    """Get requirements for disabling 2FA"""
    user = request.user
    
    if not user.two_factor_enabled:
        return Response({
            'message': '2FA is not enabled for this account'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'To disable 2FA, you need to provide:',
        'requirements': [
            {
                'field': 'password',
                'description': 'Your account password',
                'required': True
            },
            {
                'field': 'totp_code',
                'description': '6-digit code from your authenticator app (Google Authenticator, Authy, etc.)',
                'required': 'Either this OR backup_code'
            },
            {
                'field': 'backup_code',
                'description': '8-character backup code (alternative to TOTP)',
                'required': 'Either this OR totp_code'
            }
        ],
        'example_request': {
            'password': 'your_account_password',
            'totp_code': '123456'
        },
        'backup_codes_remaining': len(user.backup_codes) if user.backup_codes else 0
    }, status=status.HTTP_200_OK)





   
   
  

    

# User Profile Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user



    

# Artist Profile Views
class ArtistProfileViewSet(ModelViewSet):
    """Artist profile CRUD operations"""
    queryset = ArtistProfile.objects.select_related('user').prefetch_related('user__reviews')
    serializer_class = ArtistProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['experience_level', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'skills']
    ordering_fields = ['rating', 'total_projects_completed', 'hourly_rate']
    ordering = ['-rating']
    
    lookup_field = 'user_id'



    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ArtistProfileUpdateSerializer
        return ArtistProfileSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get artist reviews"""
        artist_profile = self.get_object()
        reviews = Review.objects.filter(artist=artist_profile.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def artworks(self, request, pk=None):
        """Get artist artworks"""
        artist_profile = self.get_object()
        artworks = Artwork.objects.filter(artist=artist_profile.user, is_available=True)
        page = self.paginate_queryset(artworks)
        if page is not None:
            serializer = ArtworkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ArtworkListSerializer(artworks, many=True)
        return Response(serializer.data)




class BuyerProfileViewSet(ModelViewSet):
    """Buyer profile CRUD operations"""
    queryset = BuyerProfile.objects.select_related('user')
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user_id'

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to calculate total_spent and projects_posted before returning data"""
        instance = self.get_object()
        # Calculate and update total_spent before returning
        instance.calculate_total_spent()
        # Also update projects_posted count
        instance.projects_posted = instance.user.posted_jobs.count()
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BuyerProfileUpdateSerializer
        return BuyerProfileSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=True, methods=['get'])
    def purchases(self, request, user_id=None):
        """Get buyer's purchase history including orders and payments"""
        buyer_profile = self.get_object()
        user = buyer_profile.user
        
        # Get orders (artwork/equipment purchases)
        orders = user.buyer_orders.all().order_by('-created_at')
        orders_data = OrderSerializer(orders, many=True).data
        
        # Get payments (job/artist hiring payments)
        payments = user.buyer_payments.all().order_by('-created_at')
        payments_data = PaymentSerializer(payments, many=True).data
        
        return Response({
            'orders': orders_data,
            'payments': payments_data,
            'total_orders': orders.count(),
            'total_payments': payments.count(),
            'completed_orders': orders.filter(status='completed').count(),
            'completed_payments': payments.filter(status='completed').count(),
        })

# Category Views
class CategoryViewSet(ReadOnlyModelViewSet):
    """Category read-only operations"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
  
 
    

  
    

# Artwork Views
from rest_framework.parsers import MultiPartParser, FormParser

class ArtworkViewSet(ModelViewSet):
    """Artwork CRUD operations"""
    queryset = Artwork.objects.select_related('artist', 'category').filter(is_available=True)
    serializer_class = ArtworkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'artwork_type', 'is_featured']
    search_fields = ['title', 'description', 'artist__username']
    ordering_fields = ['price', 'created_at', 'views_count', 'likes_count']
    ordering = ['-created_at']
    
    
    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id:
            queryset = self.queryset.filter(artist__id=user_id)
        else:
            queryset = self.queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArtworkListSerializer
        return ArtworkSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsArtistOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]
    
    def create(self, request, *args, **kwargs):
        """Create artwork with duplicate detection"""
        # Validate user is artist
        if request.user.user_type != 'artist':
            return Response(
                {'error': 'Only artists can upload artworks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check for duplicates before creating artwork
        image_file = request.FILES.get('image')
        if image_file:
            # Check for duplicates with similarity threshold of 5
            # You can adjust this value: 
            # 1-3 = Very strict (only exact duplicates)
            # 4-6 = Strict (recommended for production)
            # 7-10 = Moderate 
            # 11+ = Lenient
            duplicates = Artwork.find_duplicates_for_image(image_file, similarity_threshold=5)
            
            if duplicates:
                # Found potential duplicates - return warning with details
                duplicate_details = []
                for dup in duplicates[:3]:  # Show top 3 most similar
                    duplicate_details.append({
                        'artwork_id': dup['artwork'].id,
                        'title': dup['title'],
                        'artist': dup['artist'],
                        'similarity_percentage': dup['similarity_percentage'],
                        'upload_date': dup['upload_date'].strftime('%Y-%m-%d'),
                        'image_url': dup['artwork'].image.url if dup['artwork'].image else None
                    })
                
                return Response({
                    'error': 'Duplicate artwork detected',
                    'message': 'This image appears to be very similar to existing artworks. Please upload original content only.',
                    'duplicate_count': len(duplicates),
                    'similar_artworks': duplicate_details,
                    'action_required': 'Please choose a different image or confirm this is your original work'
                }, status=status.HTTP_409_CONFLICT)
        
        # No duplicates found, proceed with creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        artwork = serializer.save(artist=request.user)
        
        # Prepare response
        response_data = {
            'message': 'Artwork uploaded successfully',
            'artwork': ArtworkSerializer(artwork).data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update artwork"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check ownership
        if instance.artist != request.user:
            return Response(
                {'error': 'You can only update your own artworks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update fields
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        response_data = {
            'message': 'Artwork updated successfully',
            'artwork': ArtworkSerializer(instance).data
        }
        
        return Response(response_data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete artwork"""
        instance = self.get_object()
        
        # Check ownership
        if instance.artist != request.user:
            return Response(
                {'error': 'You can only delete your own artworks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete from database
        instance.delete()
        
        return Response({
            'message': 'Artwork deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    

    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment views"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike artwork - each user can like only once"""
        artwork = self.get_object()
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to like artworks'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Toggle like for the user
        liked, likes_count = artwork.toggle_like(request.user)
        
        return Response({
            'liked': liked,
            'likes_count': likes_count,
            'message': 'Artwork liked!' if liked else 'Artwork unliked!'
        })
    
    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        """Get users who liked this artwork"""
        artwork = self.get_object()
        likes = artwork.user_likes.select_related('user').all()
        
        users_data = []
        for like in likes:
            users_data.append({
                'user_id': like.user.id,
                'username': like.user.username,
                'first_name': like.user.first_name,
                'last_name': like.user.last_name,
                'liked_at': like.created_at
            })
        
        return Response({
            'total_likes': len(users_data),
            'users': users_data
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured artworks"""
        featured_artworks = self.queryset.filter(is_featured=True)
        page = self.paginate_queryset(featured_artworks)
        if page is not None:
            serializer = ArtworkListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ArtworkListSerializer(featured_artworks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def check_duplicate(self, request):
        """Check if uploaded image is duplicate before saving"""
        if request.user.user_type != 'artist':
            return Response(
                {'error': 'Only artists can check for duplicates'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'error': 'Image file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for duplicates
        similarity_threshold = int(request.data.get('similarity_threshold', 5))
        duplicates = Artwork.find_duplicates_for_image(image_file, similarity_threshold)
        
        if duplicates:
            duplicate_details = []
            for dup in duplicates:
                duplicate_details.append({
                    'artwork_id': dup['artwork'].id,
                    'title': dup['title'],
                    'artist': dup['artist'],
                    'similarity_percentage': dup['similarity_percentage'],
                    'similarity_score': dup['similarity_score'],
                    'upload_date': dup['upload_date'].strftime('%Y-%m-%d %H:%M'),
                    'image_url': dup['artwork'].image.url if dup['artwork'].image else None
                })
            
            return Response({
                'is_duplicate': True,
                'duplicate_count': len(duplicates),
                'similar_artworks': duplicate_details,
                'message': f'Found {len(duplicates)} similar artwork(s)',
                'recommendation': 'Consider uploading original content only'
            })
        else:
            return Response({
                'is_duplicate': False,
                'message': 'No similar artworks found. Safe to upload!',
                'duplicate_count': 0
            })
    
    @action(detail=True, methods=['get'])
    def find_similar(self, request, pk=None):
        """Find artworks similar to this one"""
        artwork = self.get_object()
        similarity_threshold = int(request.GET.get('threshold', 10))
        
        similar_artworks = artwork.check_for_duplicates(similarity_threshold)
        
        similar_data = []
        for similar in similar_artworks:
            similar_data.append({
                'artwork': ArtworkListSerializer(similar['artwork']).data,
                'similarity_percentage': similar['similarity_percentage'],
                'similarity_score': similar['similarity_score']
            })
        
        return Response({
            'artwork_id': artwork.id,
            'artwork_title': artwork.title,
            'similar_count': len(similar_data),
            'similar_artworks': similar_data,
            'threshold_used': similarity_threshold
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def force_upload(self, request):
        """Force upload artwork even if duplicates are detected (with confirmation)"""
        if request.user.user_type != 'artist':
            return Response(
                {'error': 'Only artists can upload artworks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user confirmed they want to upload despite duplicates
        confirm_upload = request.data.get('confirm_duplicate_upload', False)
        if not confirm_upload:
            return Response(
                {'error': 'You must confirm that you want to upload despite duplicate detection'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create artwork without duplicate checking
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        artwork = serializer.save(artist=request.user)
        
        return Response({
            'message': 'Artwork uploaded successfully (duplicate check bypassed)',
            'artwork': ArtworkSerializer(artwork).data,
            'warning': 'This artwork was uploaded despite potential duplicates being detected'
        }, status=status.HTTP_201_CREATED)
    
    
def create_notification(recipient, notification_type, title, message):
    """Helper function to create notifications"""
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message
    )
    
    
class JobViewSet(ModelViewSet):
    """Job/Project CRUD operations"""
    queryset = Job.objects.select_related('buyer', 'category', 'hired_artist').prefetch_related('bids')
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'experience_level', 'status']
    search_fields = ['title', 'description', 'required_skills']
    ordering_fields = ['budget_min', 'budget_max', 'deadline', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsBuyerOrReadOnly()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        """Filter jobs for list view (only open jobs)."""
        queryset = self.queryset
        if self.action == 'list':
            queryset = queryset.filter(status='open')
        return queryset
    

    # --------------------------------------------------
    #              GET JOB BIDS
    # --------------------------------------------------
    @action(detail=True, methods=['get'])
    def bids(self, request, pk=None):
        """Get job bids"""
        job = self.get_object()
        bids = job.bids.select_related('artist').all()
        page = self.paginate_queryset(bids)
        if page is not None:
            serializer = BidListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BidListSerializer(bids, many=True)
        return Response(serializer.data)


    # --------------------------------------------------
    #              HIRE ARTIST (WITH EMAILS)
    # --------------------------------------------------
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def hire_artist(self, request, pk=None):
        """Hire an artist for the job after verifying payment"""
        job = self.get_object()
        bid_id = request.data.get('bid_id')

        if job.buyer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        if job.status != 'open':
            return Response({'error': 'Job is not open'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bid = Bid.objects.get(id=bid_id, job=job)

            # Step 1: Verify payment
            payment = Payment.objects.filter(
                payer=request.user,
                job=job,
                payee=bid.artist,
                status='completed',
                hire_status='pending'
            ).first()

            if not payment:
                return Response({
                    'error': 'Payment not completed for this job. Please pay first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Hire artist
            job.hired_artist = bid.artist
            job.status = 'in_progress'
            job.final_amount = bid.bid_amount
            job.save()

            bid.status = 'accepted'
            bid.save()

            # Reject all other bids
            job.bids.exclude(id=bid_id).update(status='rejected')

            # Step 3: Create contract
            contract = Contract.objects.create(
                job=job,
                artist=bid.artist,
                buyer=request.user,
                terms=f"Contract for project: {job.title}\n\nDelivery Time: {bid.delivery_time} days\nAmount: PKR{bid.bid_amount}\n\nArtist will deliver based on requirements.",
                rights_type='display_only',
                amount=bid.bid_amount,
                deadline=timezone.now() + timezone.timedelta(days=bid.delivery_time),
                status='pending'
            )
            
            # Email notifications about contract creation to both parties
            send_contract_notification_email(contract, 'created', 'artist')
            send_contract_notification_email(contract, 'created', 'buyer')

            # --------------------------------------------------
            #                NOTIFICATIONS (APP)
            # --------------------------------------------------
            create_notification(
                recipient=bid.artist,
                notification_type='bid_accepted',
                title='Your bid was accepted!',
                message=f'Your bid for "{job.title}" has been accepted.'
            )

            create_notification(
                recipient=request.user,
                notification_type='bid_accepted',
                title='Artist Hired Successfully',
                message=f'You hired {bid.artist.username} for "{job.title}".'
            )

            # Notify rejected artists
            rejected_bids = job.bids.filter(status='rejected')
            for rejected_bid in rejected_bids:
                create_notification(
                    recipient=rejected_bid.artist,
                    notification_type='bid_rejected',
                    title='Bid Not Selected',
                    message=f'Your bid for "{job.title}" was not selected.'
                )

            # --------------------------------------------------
            #            EMAIL NOTIFICATIONS
            # --------------------------------------------------

            # Email to Artist (Bid Accepted)
            send_notification_email(
                subject="Your Bid Was Accepted!",
                message=f"Good news! Your bid for '{job.title}' has been accepted. Please sign the contract.",
                recipient_email=bid.artist.email
            )

            # Email to Buyer (Confirmation)
            send_notification_email(
                subject="Artist Hired Successfully",
                message=f"You hired {bid.artist.username} for the job '{job.title}'.",
                recipient_email=request.user.email
            )

            # Email to Rejected Artists
            for rejected_bid in rejected_bids:
                send_notification_email(
                    subject="Bid Not Selected",
                    message=f"Unfortunately, your bid for '{job.title}' was not selected.",
                    recipient_email=rejected_bid.artist.email
                )

            return Response({
                'message': 'Artist hired successfully after verifying payment',
                'payment_id': payment.id,
                'contract_id': contract.id,
                'payment_status': payment.status,
                'hire_status': payment.hire_status,
                'transaction_id': payment.transaction_id,
                'amount': str(payment.amount)
            })

        except Bid.DoesNotExist:
            return Response({'error': 'Bid not found'}, status=status.HTTP_404_NOT_FOUND)



    # --------------------------------------------------
    #                COMPLETE JOB (WITH EMAILS)
    # --------------------------------------------------
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete_job(self, request, pk=None):
        """Complete a job"""
        job = self.get_object()
        
        if job.buyer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if job.status != 'in_progress':
            return Response({'error': 'Job is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update job status
        job.status = 'completed'
        job.save()
        
        # Update contract status to completed
        try:
            contract = job.contract
            contract.status = 'completed'
            contract.save()
            
            # Send contract completion emails
            send_contract_notification_email(contract, 'completed', 'artist')
            send_contract_notification_email(contract, 'completed', 'buyer')
        except Contract.DoesNotExist:
            pass  # No contract exists for this job
        
        # Release payment
        payment = Payment.objects.filter(job=job, payer=request.user, payee=job.hired_artist).first()
        if payment:
            payment.hire_status = 'released'
            payment.save()

        # Update artist profile
        if job.hired_artist:
            artist_profile = job.hired_artist.artist_profile
            artist_profile.total_projects_completed += 1
            artist_profile.total_earnings += job.final_amount or 0
            artist_profile.save()

        # Update buyer profile
        buyer_profile = job.buyer.buyer_profile
        buyer_profile.calculate_total_spent()

        # --------------------------------------------------
        #            EMAIL NOTIFICATIONS
        # --------------------------------------------------

        # Email to Artist
        send_notification_email(
            subject="Job Completed",
            message=f"The job '{job.title}' has been marked as completed. Your payment has been released.",
            recipient_email=job.hired_artist.email
        )

        # Email to Buyer
        send_notification_email(
            subject="Job Completed Successfully",
            message=f"You successfully completed the job '{job.title}'.",
            recipient_email=request.user.email
        )
        
        return Response({
            'message': 'Job completed successfully',
            'job_status': job.status,
            'payment_hire_status': payment.hire_status if payment else None
        })






# Bid Views
class BidViewSet(ModelViewSet):
    """Bid CRUD operations"""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['bid_amount', 'delivery_time', 'created_at']
    ordering = ['bid_amount']
    
    def get_queryset(self):
        """Filter bids based on user"""
        user = self.request.user
        if user.user_type == 'artist':
            return Bid.objects.filter(artist=user).select_related('job', 'artist')
        elif user.user_type == 'buyer':
            return Bid.objects.filter(job__buyer=user).select_related('job', 'artist')
        return Bid.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BidListSerializer
        return BidSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsArtistOrReadOnly()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        job = serializer.validated_data['job']  # now safe, always present

        # Check if job is still open
        if job.status != 'open':
            raise serializers.ValidationError("Job is no longer open for bidding")

        # Check if artist already bid
        if Bid.objects.filter(job=job, artist=self.request.user).exists():
            raise serializers.ValidationError("You have already bid on this job")

        serializer.save(artist=self.request.user)


        
        
        

# Equipment Views
class EquipmentViewSet(ModelViewSet):
    """Equipment CRUD operations"""
    queryset = Equipment.objects.filter(is_available=True)
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment_type', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Only authenticated users can manage equipment
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get equipment that is in stock"""
        in_stock_equipment = self.queryset.filter(stock_quantity__gt=0)
        page = self.paginate_queryset(in_stock_equipment)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(in_stock_equipment, many=True)
        return Response(serializer.data)
    


# Order Views
class OrderViewSet(ModelViewSet):
    """Order CRUD operations"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order_type', 'status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter orders by current user"""
        return Order.objects.filter(buyer=self.request.user).prefetch_related(
            'artwork_items__artwork', 'equipment_items__equipment'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an order"""
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'confirmed'
            order.save()
            
            # Reduce equipment stock
            for item in order.equipment_items.all():
                item.equipment.reduce_stock(item.quantity)
            
            return Response({'message': 'Order confirmed successfully'})
        return Response({'error': 'Order cannot be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Order cancelled successfully'})
        return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(ModelViewSet):
    """Payment CRUD operations with Stripe integration"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'status']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter payments by current user"""
        user = self.request.user
        return Payment.objects.filter(
            Q(payer=user) | Q(payee=user)
        ).select_related('payer', 'payee', 'order', 'job')

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a payment using Stripe"""
        payment = self.get_object()
        if payment.payer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        if payment.status != 'pending':
            return Response({'error': 'Payment already processed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create Stripe PaymentIntent with automatic confirmation for better frontend compatibility
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Stripe works in cents
                currency="pkr",  # Changed to PKR
                payment_method_types=["card"],
                confirmation_method="automatic",  # Automatic confirmation works better with Stripe.js
                metadata={
                    "payment_id": payment.id,
                    "payer_id": payment.payer.id,
                    "payee_id": payment.payee.id if payment.payee else None,
                    "amount_pkr": str(payment.amount)
                }
            )

            payment.stripe_payment_intent = intent['id']
            payment.status = 'processing'
            payment.save()

            return Response({
                'client_secret': intent['client_secret'],
                'payment_intent_id': intent['id'],
                'requires_action': intent.get('next_action') is not None,
                'message': 'Stripe PaymentIntent created successfully. Use client_secret with Stripe.js'
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirm payment status after frontend processing"""
        payment = self.get_object()
        
        if payment.payer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if payment.status not in ['processing', 'pending']:
            return Response({'error': 'Payment cannot be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check the PaymentIntent status from Stripe
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent)
            
            if intent.status == 'succeeded':
                # Payment successful
                payment.status = 'completed'
                payment.save()
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_id': payment.transaction_id,
                    'status': payment.status,
                    'message': 'Payment completed successfully'
                }, status=status.HTTP_200_OK)
            
            elif intent.status == 'requires_action':
                return Response({
                    'requires_action': True,
                    'client_secret': intent.client_secret,
                    'next_action': intent.next_action,
                    'message': 'Please complete 3D Secure verification'
                }, status=status.HTTP_200_OK)
            
            elif intent.status == 'processing':
                return Response({
                    'processing': True,
                    'message': 'Payment is being processed'
                }, status=status.HTTP_200_OK)
            
            else:
                # Payment failed
                payment.status = 'failed'
                payment.save()
                
                return Response({
                    'error': f'Payment failed with status: {intent.status}',
                    'status': intent.status
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def handle_3d_secure(self, request, pk=None):
        """Handle 3D Secure completion"""
        payment = self.get_object()
        
        if payment.payer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Retrieve the latest PaymentIntent status
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent)
            
            if intent.status == 'succeeded':
                payment.status = 'completed'
                payment.save()
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_id': payment.transaction_id,
                    'status': payment.status,
                    'message': '3D Secure verification completed successfully'
                }, status=status.HTTP_200_OK)
            
            elif intent.status == 'requires_action':
                return Response({
                    'requires_action': True,
                    'client_secret': intent.client_secret,
                    'message': 'Still requires 3D Secure verification'
                }, status=status.HTTP_200_OK)
            
            else:
                payment.status = 'failed'
                payment.save()
                
                return Response({
                    'error': f'Payment failed with status: {intent.status}',
                    'status': intent.status
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def hire_artist_payment(self, request):
        """
        💳 Pay an artist for a job and assign artist automatically
        - Accepts a bid, assigns artist to job, and processes Stripe payment
        - Hire status remains 'pending' until job completed
        """
        job_id = request.data.get('job_id')
        bid_id = request.data.get('bid_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'stripe')

        if not job_id or not bid_id or not amount:
            return Response({'error': 'Job ID, Bid ID, and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure requester is the job buyer
        if job.buyer != request.user:
            return Response({'error': 'You are not authorized to pay for this job'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure job is open
        if job.status != 'open':
            return Response({'error': 'Job is not open for hiring'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bid = Bid.objects.get(id=bid_id, job=job)
        except Bid.DoesNotExist:
            return Response({'error': 'Bid not found'}, status=status.HTTP_404_NOT_FOUND)

        # 🔹 Step 1: Assign the artist and update job
        job.hired_artist = bid.artist
        job.status = 'in_progress'
        job.final_amount = Decimal(amount)
        job.save()

        # Update bid statuses
        bid.status = 'accepted'
        bid.save()
        job.bids.exclude(id=bid_id).update(status='rejected')

        try:
            # 🔹 Step 2: Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(Decimal(amount) * 100),  # Stripe uses cents
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "job_id": job.id,
                    "buyer_id": request.user.id,
                    "artist_id": bid.artist.id,
                    "bid_id": bid.id
                }
            )

            # 🔹 Step 3: Create Payment record
            status_val = 'completed' if intent['status'] == 'succeeded' else 'pending'
            payment = Payment.objects.create(
                payer=request.user,
                payee=bid.artist,
                job=job,
                amount=Decimal(amount),
                payment_method=payment_method,
                status=status_val,
                hire_status='pending',
                stripe_payment_intent=intent['id']
            )

            return Response({
                "message": "Payment successful and artist hired. Hire payment pending release.",
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "payment_status": payment.status,
                "hire_status": payment.hire_status,
                "job_status": job.status,
                "hired_artist": bid.artist.username,
                "bid_status": bid.status
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm_stripe_payment(self, request):
        """Confirm Stripe payment — mark as completed, hire payment stays pending"""
        payment_intent_id = request.data.get('payment_intent_id')

        if not payment_intent_id:
            return Response({'error': 'Payment Intent ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 🔹 Retrieve PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # ✅ If Stripe confirms success
            if intent['status'] == 'succeeded':
                payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)

                # ✅ Stripe payment done
                payment.status = 'completed'

                # ✅ Keep hire payment pending until work is done
                if payment.job:
                    payment.hire_status = 'pending'

                payment.save()

                # ✅ Optionally update job state
                if payment.job:
                    payment.job.status = 'in_progress'
                    payment.job.save()

                return Response({
                    'message': 'Stripe payment confirmed successfully',
                    'payment_id': payment.id,
                    'transaction_id': payment.transaction_id,
                    'status': payment.status,
                    'hire_status': payment.hire_status
                }, status=status.HTTP_200_OK)

            # 🕒 If still processing or requires action
            return Response({'status': intent['status']}, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    # ✅ ADD THIS METHOD
    def create(self, request, *args, **kwargs):
        """Create payment record and return full details (with transaction_id)"""
        create_serializer = PaymentCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        create_serializer.is_valid(raise_exception=True)
        payment = create_serializer.save()  # payer auto-set here

        # Return full details (including transaction_id, platform fee, etc.)
        full_serializer = PaymentSerializer(payment, context={'request': request})
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    





# Message Views
class MessageViewSet(ModelViewSet):
    """Message CRUD operations"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'job']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter messages by current user"""
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver', 'job')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark message as read"""
        message = self.get_object()
        if message.receiver == request.user:
            message.mark_as_read()
            return Response({'message': 'Message marked as read'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get user conversations"""
        user = request.user
        # Get latest message from each conversation
        conversations = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).values('sender', 'receiver').annotate(
            latest_message_time=models.Max('created_at')
        ).order_by('-latest_message_time')
        
        return Response(conversations)



# Review Views
class ReviewViewSet(ModelViewSet):
    """Review CRUD operations"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter reviews based on user type"""
        user = self.request.user
        if user.user_type == 'buyer':
            return Review.objects.filter(reviewer=user).select_related('artist', 'job')
        elif user.user_type == 'artist':
            return Review.objects.filter(artist=user).select_related('reviewer', 'job')
        return Review.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        """Create review with validations"""
        job = serializer.validated_data['job']
        
        # Check if job is completed
        if job.status != 'completed':
            raise serializers.ValidationError("Can only review completed jobs")
        
        # Check if user is the buyer of the job
        if job.buyer != self.request.user:
            raise serializers.ValidationError("Only job buyer can leave a review")
        
        # Check if review already exists
        if Review.objects.filter(reviewer=self.request.user, job=job).exists():
            raise serializers.ValidationError("Review already exists for this job")
        
        review = serializer.save()
        
        # Update artist rating
        review.artist.artist_profile.calculate_rating()
        
        
    
# Contract Views
class ContractViewSet(ModelViewSet):
    """Contract CRUD operations"""
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'rights_type']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter contracts by current user"""
        user = self.request.user
        return Contract.objects.filter(
            Q(artist=user) | Q(buyer=user)
        ).select_related('job', 'artist', 'buyer')
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign a contract"""
        contract = self.get_object()
        user = request.user
        
        if user == contract.artist and not contract.artist_signed:
            contract.sign_by_artist()
            
            # Email to buyer about artist signing
            send_contract_notification_email(contract, 'signed_by_artist', 'buyer')
            
            # Check if contract is now fully signed
            if contract.is_fully_signed():
                # Email to both parties about contract activation
                send_contract_notification_email(contract, 'activated', 'artist')
                send_contract_notification_email(contract, 'activated', 'buyer')
            
            return Response({
                'message': 'Contract signed by artist',
                'contract_status': contract.status,
                'is_fully_signed': contract.is_fully_signed()
            })
            
        elif user == contract.buyer and not contract.buyer_signed:
            contract.sign_by_buyer()
            
            # Email to artist about buyer signing
            send_contract_notification_email(contract, 'signed_by_buyer', 'artist')
            
            # Check if contract is now fully signed
            if contract.is_fully_signed():
                # Email to both parties about contract activation
                send_contract_notification_email(contract, 'activated', 'artist')
                send_contract_notification_email(contract, 'activated', 'buyer')
            
            return Response({
                'message': 'Contract signed by buyer',
                'contract_status': contract.status,
                'is_fully_signed': contract.is_fully_signed()
            })
            
        else:
            return Response({'error': 'Cannot sign contract'}, status=status.HTTP_400_BAD_REQUEST)
   
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a contract"""
        contract = self.get_object()
        user = request.user
        
        # Only allow termination by contract parties and if contract is active
        if user not in [contract.artist, contract.buyer]:
            return Response({'error': 'Not authorized to terminate this contract'}, status=status.HTTP_403_FORBIDDEN)
        
        if contract.status not in ['active', 'pending']:
            return Response({'error': 'Contract cannot be terminated in current status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update contract status
        contract.status = 'terminated'
        contract.save()
        
        # Update related job status if exists
        if hasattr(contract, 'job') and contract.job.status == 'in_progress':
            contract.job.status = 'cancelled'
            contract.job.save()
        
        # Send termination emails to both parties
        send_contract_notification_email(contract, 'terminated', 'artist')
        send_contract_notification_email(contract, 'terminated', 'buyer')
        
        return Response({
            'message': 'Contract terminated successfully',
            'contract_status': contract.status,
            'terminated_by': user.username
        })
    
# Notification Views
class NotificationViewSet(ReadOnlyModelViewSet):
    """Notification read operations"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notifications by current user"""
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notifications count"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})



# Analytics Views (Admin only)
class PlatformAnalyticsViewSet(ReadOnlyModelViewSet):
    """Platform analytics for admin"""
    queryset = PlatformAnalytics.objects.all()
    serializer_class = PlatformAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only allow admin users to access analytics"""
        if self.request.user.user_type == 'admin' or self.request.user.is_staff:
            return self.queryset
        return PlatformAnalytics.objects.none()
    
    @action(detail=False, methods=['post'])
    def calculate_today(self, request):
        """Calculate today's analytics"""
        if request.user.user_type != 'admin' and not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now().date()
        analytics, created = PlatformAnalytics.objects.get_or_create(date=today)
        analytics.calculate_daily_stats()
        
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)



# Dashboard Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for current user"""
    user = request.user
    stats = {}

    if user.user_type == 'artist':
        artist_profile, _ = ArtistProfile.objects.get_or_create(user=user)
        stats = {
            'total_projects': artist_profile.total_projects_completed,
            'total_earnings': artist_profile.total_earnings,
            'current_rating': artist_profile.rating,
            'active_bids': user.my_bids.filter(status='pending').count(),
            'ongoing_projects': user.hired_projects.filter(status='in_progress').count(),
            'total_artworks': user.artworks.filter(is_available=True).count(),
            'recent_reviews': list(
                user.reviews.order_by('-created_at')[:5].values('rating', 'comment', 'created_at')
            ),
        }

    elif user.user_type == 'buyer':
        buyer_profile, _ = BuyerProfile.objects.get_or_create(user=user)
        stats = {
            'total_spent': buyer_profile.total_spent,
            'projects_posted': buyer_profile.projects_posted,
            'active_jobs': user.posted_jobs.filter(status='open').count(),
            'ongoing_projects': user.posted_jobs.filter(status='in_progress').count(),
            'total_orders': user.buyer_orders.count(),
            'pending_payments': user.buyer_payments.filter(status='pending').count(),
        }

    elif user.user_type == 'admin':
        stats = {
            'total_users': CustomUser.objects.count(),
            'total_artists': CustomUser.objects.filter(user_type='artist').count(),
            'total_buyers': CustomUser.objects.filter(user_type='buyer').count(),
            'active_jobs': Job.objects.filter(status='open').count(),
            'completed_jobs': Job.objects.filter(status='completed').count(),
            'total_revenue': Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'recent_registrations': list(
                CustomUser.objects.order_by('-created_at')[:10]
                .values('id', 'username', 'email', 'user_type', 'created_at')
            ),
        }

    return Response(stats)
# Search Views
@api_view(['GET'])
@permission_classes([AllowAny])
def global_search(request):
    """Global search across artworks, jobs, and artists"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Search artworks
    artworks = Artwork.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(artist__username__icontains=query),
        is_available=True
    )[:10]
    
    # Search jobs
    jobs = Job.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(required_skills__icontains=query),
        status='open'
    )[:10]
    
    # Search artists
    artists = ArtistProfile.objects.filter(
        Q(user__username__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(skills__icontains=query),
        is_available=True
    )[:10]
    
    results = {
        'artworks': ArtworkListSerializer(artworks, many=True).data,
        'jobs': JobListSerializer(jobs, many=True).data,
        'artists': ArtistProfileSerializer(artists, many=True).data,
        'query': query
    }
    
    return Response(results)





