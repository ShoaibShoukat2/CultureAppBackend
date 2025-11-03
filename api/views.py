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
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsArtistOrReadOnly, IsBuyerOrReadOnly


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
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
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

    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return BuyerProfileUpdateSerializer
        return BuyerProfileSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

# Category Views
class CategoryViewSet(ReadOnlyModelViewSet):
    """Category read-only operations"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
  
 
    

  
    

# Artwork Views
class ArtworkViewSet(ModelViewSet):
    """Artwork CRUD operations"""
    queryset = Artwork.objects.select_related('artist', 'category').filter(is_available=True)
    serializer_class = ArtworkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
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
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment views"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike artwork"""
        artwork = self.get_object()
        # Simple like increment (you can implement user-specific likes)
        artwork.likes_count += 1
        artwork.save()
        return Response({'likes_count': artwork.likes_count})
    
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
    

    

# Job Views
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
        """Filter jobs based on user type and status"""
        queryset = self.queryset
        if self.action == 'list':
            # Only show open jobs in list view
            queryset = queryset.filter(status='open')
        return queryset
    
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def hire_artist(self, request, pk=None):
        """Hire an artist for the job"""
        job = self.get_object()
        bid_id = request.data.get('bid_id')
        
        if job.buyer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if job.status != 'open':
            return Response({'error': 'Job is not open'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bid = Bid.objects.get(id=bid_id, job=job)
            job.hired_artist = bid.artist
            job.status = 'in_progress'
            job.final_amount = bid.bid_amount
            job.save()
            
            bid.status = 'accepted'
            bid.save()
            
            # Reject other bids
            job.bids.exclude(id=bid_id).update(status='rejected')
            
            return Response({'message': 'Artist hired successfully'})
        except Bid.DoesNotExist:
            return Response({'error': 'Bid not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete_job(self, request, pk=None):
        """Complete a job"""
        job = self.get_object()
        
        if job.buyer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if job.status != 'in_progress':
            return Response({'error': 'Job is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
        
        job.status = 'completed'
        job.save()
        
        # Update artist profile
        if job.hired_artist:
            artist_profile = job.hired_artist.artist_profile
            artist_profile.total_projects_completed += 1
            artist_profile.total_earnings += job.final_amount or 0
            artist_profile.save()
        
        # Update buyer profile
        buyer_profile = job.buyer.buyer_profile
        buyer_profile.calculate_total_spent()
        
        return Response({'message': 'Job completed successfully'})


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
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Stripe works in cents
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "payment_id": payment.id,
                    "payer_id": payment.payer.id,
                    "payee_id": payment.payee.id if payment.payee else None
                }
            )

            payment.stripe_payment_intent = intent['id']
            payment.status = 'processing'
            payment.save()

            return Response({
                'client_secret': intent['client_secret'],
                'message': 'Stripe PaymentIntent created successfully'
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm_stripe_payment(self, request):
        """Confirm payment after client completes card payment"""
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({'error': 'Payment Intent ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # If succeeded, mark payment as completed
            if intent['status'] == 'succeeded':
                payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)
                payment.status = 'completed'
                payment.save()

                # Update related order/job
                if payment.order:
                    payment.order.status = 'confirmed'
                    payment.order.save()

                if payment.job and payment.payee:
                    artist_profile = payment.payee.artist_profile
                    artist_profile.total_earnings += payment.calculate_artist_earning()
                    artist_profile.save()

                return Response({'message': 'Payment confirmed successfully'})

            return Response({'status': intent['status']})

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
            return Response({'message': 'Contract signed by artist'})
        elif user == contract.buyer and not contract.buyer_signed:
            contract.sign_by_buyer()
            return Response({'message': 'Contract signed by buyer'})
        else:
            return Response({'error': 'Cannot sign contract'}, status=status.HTTP_400_BAD_REQUEST)

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