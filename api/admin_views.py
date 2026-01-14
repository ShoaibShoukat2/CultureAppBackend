# admin_views.py - Comprehensive Admin Backend APIs
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal

from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly, IsArtistOrReadOnly, IsBuyerOrReadOnly

User = get_user_model()

# Custom Admin Permission
class IsAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow admin users or staff to access admin APIs.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type == 'admin' or request.user.is_staff or request.user.is_superuser)
        )

# Admin Pagination
class AdminPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

# ===== USER MANAGEMENT =====
class AdminUserManagementViewSet(ModelViewSet):
    """
    Admin User Management - Full CRUD operations for all users
    """
    queryset = CustomUser.objects.all().order_by('-created_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['created_at', 'last_login', 'username']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def verify_user(self, request, pk=None):
        """Verify a user account"""
        user = self.get_object()
        user.is_verified = True
        user.save()
        return Response({'message': f'User {user.username} verified successfully'})

    @action(detail=True, methods=['post'])
    def unverify_user(self, request, pk=None):
        """Unverify a user account"""
        user = self.get_object()
        user.is_verified = False
        user.save()
        return Response({'message': f'User {user.username} unverified'})

    @action(detail=True, methods=['post'])
    def activate_user(self, request, pk=None):
        """Activate a user account"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': f'User {user.username} activated'})

    @action(detail=True, methods=['post'])
    def deactivate_user(self, request, pk=None):
        """Deactivate a user account"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': f'User {user.username} deactivated'})

    @action(detail=True, methods=['post'])
    def make_staff(self, request, pk=None):
        """Make user staff"""
        user = self.get_object()
        user.is_staff = True
        user.save()
        return Response({'message': f'User {user.username} is now staff'})

    @action(detail=True, methods=['post'])
    def remove_staff(self, request, pk=None):
        """Remove staff privileges"""
        user = self.get_object()
        user.is_staff = False
        user.save()
        return Response({'message': f'Staff privileges removed from {user.username}'})

    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """Get user statistics"""
        stats = {
            'total_users': CustomUser.objects.count(),
            'verified_users': CustomUser.objects.filter(is_verified=True).count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'artists': CustomUser.objects.filter(user_type='artist').count(),
            'buyers': CustomUser.objects.filter(user_type='buyer').count(),
            'admins': CustomUser.objects.filter(user_type='admin').count(),
            'staff_users': CustomUser.objects.filter(is_staff=True).count(),
            'recent_registrations': CustomUser.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        return Response(stats)

# ===== ARTWORK MANAGEMENT =====
class AdminArtworkManagementViewSet(ModelViewSet):
    """
    Admin Artwork Management - Manage all artworks with moderation
    """
    queryset = Artwork.objects.all().select_related('artist', 'category').order_by('-created_at')
    serializer_class = ArtworkSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artwork_type', 'is_available', 'is_featured', 'category']
    search_fields = ['title', 'description', 'artist__username']
    ordering_fields = ['created_at', 'price', 'views_count', 'likes_count']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def feature_artwork(self, request, pk=None):
        """Feature an artwork"""
        artwork = self.get_object()
        artwork.is_featured = True
        artwork.save()
        return Response({'message': f'Artwork "{artwork.title}" featured successfully'})

    @action(detail=True, methods=['post'])
    def unfeature_artwork(self, request, pk=None):
        """Unfeature an artwork"""
        artwork = self.get_object()
        artwork.is_featured = False
        artwork.save()
        return Response({'message': f'Artwork "{artwork.title}" unfeatured'})

    @action(detail=True, methods=['post'])
    def approve_artwork(self, request, pk=None):
        """Approve an artwork"""
        artwork = self.get_object()
        artwork.is_available = True
        artwork.save()
        return Response({'message': f'Artwork "{artwork.title}" approved'})

    @action(detail=True, methods=['post'])
    def reject_artwork(self, request, pk=None):
        """Reject an artwork"""
        artwork = self.get_object()
        artwork.is_available = False
        artwork.save()
        return Response({'message': f'Artwork "{artwork.title}" rejected'})

    @action(detail=False, methods=['get'])
    def artwork_stats(self, request):
        """Get artwork statistics"""
        stats = {
            'total_artworks': Artwork.objects.count(),
            'available_artworks': Artwork.objects.filter(is_available=True).count(),
            'featured_artworks': Artwork.objects.filter(is_featured=True).count(),
            'pending_review': 0,  # No longer using AI review
            'total_views': Artwork.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'total_likes': Artwork.objects.aggregate(Sum('likes_count'))['likes_count__sum'] or 0,
            'average_price': Artwork.objects.aggregate(Avg('price'))['price__avg'] or 0,
            'recent_uploads': Artwork.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        return Response(stats)

# ===== JOB MANAGEMENT =====
class AdminJobManagementViewSet(ModelViewSet):
    """
    Admin Job Management - Manage all jobs and projects
    """
    queryset = Job.objects.all().select_related('buyer', 'category', 'hired_artist').order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'experience_level', 'category']
    search_fields = ['title', 'description', 'buyer__username', 'hired_artist__username']
    ordering_fields = ['created_at', 'budget_min', 'budget_max', 'deadline']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def close_job(self, request, pk=None):
        """Close a job (admin action)"""
        job = self.get_object()
        job.status = 'cancelled'
        job.save()
        return Response({'message': f'Job "{job.title}" closed by admin'})

    @action(detail=True, methods=['post'])
    def reopen_job(self, request, pk=None):
        """Reopen a job"""
        job = self.get_object()
        job.status = 'open'
        job.save()
        return Response({'message': f'Job "{job.title}" reopened'})

    @action(detail=False, methods=['get'])
    def job_stats(self, request):
        """Get job statistics"""
        stats = {
            'total_jobs': Job.objects.count(),
            'open_jobs': Job.objects.filter(status='open').count(),
            'in_progress_jobs': Job.objects.filter(status='in_progress').count(),
            'completed_jobs': Job.objects.filter(status='completed').count(),
            'cancelled_jobs': Job.objects.filter(status='cancelled').count(),
            'average_budget': Job.objects.aggregate(
                avg_min=Avg('budget_min'), 
                avg_max=Avg('budget_max')
            ),
            'total_bids': Bid.objects.count(),
            'recent_jobs': Job.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        return Response(stats)

# ===== PAYMENT MANAGEMENT =====
class AdminPaymentManagementViewSet(ModelViewSet):
    """
    Admin Payment Management - Monitor and manage all payments
    """
    queryset = Payment.objects.all().select_related('payer', 'payee', 'order', 'job').order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'status', 'hire_status']
    search_fields = ['transaction_id', 'payer__username', 'payee__username']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def refund_payment(self, request, pk=None):
        """Refund a payment (admin action)"""
        payment = self.get_object()
        if payment.status == 'completed':
            payment.status = 'refunded'
            payment.save()
            return Response({'message': f'Payment {payment.transaction_id} refunded'})
        return Response({'error': 'Payment cannot be refunded'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def release_payment(self, request, pk=None):
        """Release hire payment to artist"""
        payment = self.get_object()
        if payment.hire_status == 'pending':
            payment.hire_status = 'released'
            payment.save()
            return Response({'message': f'Payment {payment.transaction_id} released to artist'})
        return Response({'error': 'Payment cannot be released'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def payment_stats(self, request):
        """Get payment statistics"""
        stats = {
            'total_payments': Payment.objects.count(),
            'completed_payments': Payment.objects.filter(status='completed').count(),
            'pending_payments': Payment.objects.filter(status='pending').count(),
            'failed_payments': Payment.objects.filter(status='failed').count(),
            'refunded_payments': Payment.objects.filter(status='refunded').count(),
            'total_revenue': Payment.objects.filter(status='completed').aggregate(
                Sum('amount')
            )['amount__sum'] or 0,
            'platform_fees': Payment.objects.filter(status='completed').aggregate(
                total=Sum(F('amount') * 0.05)
            )['total'] or 0,
            'pending_releases': Payment.objects.filter(hire_status='pending').count(),
        }
        return Response(stats)

# ===== CATEGORY MANAGEMENT =====
class AdminCategoryManagementViewSet(ModelViewSet):
    """
    Admin Category Management - Full CRUD for categories
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']

    @action(detail=True, methods=['post'])
    def activate_category(self, request, pk=None):
        """Activate a category"""
        category = self.get_object()
        category.is_active = True
        category.save()
        return Response({'message': f'Category "{category.name}" activated'})

    @action(detail=True, methods=['post'])
    def deactivate_category(self, request, pk=None):
        """Deactivate a category"""
        category = self.get_object()
        category.is_active = False
        category.save()
        return Response({'message': f'Category "{category.name}" deactivated'})

# ===== EQUIPMENT MANAGEMENT =====
class AdminEquipmentManagementViewSet(ModelViewSet):
    """
    Admin Equipment Management - Full CRUD for equipment
    """
    queryset = Equipment.objects.all().order_by('-created_at')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment_type', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price', 'stock_quantity']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update equipment stock"""
        equipment = self.get_object()
        new_stock = request.data.get('stock_quantity')
        if new_stock is not None:
            equipment.stock_quantity = int(new_stock)
            equipment.save()
            return Response({'message': f'Stock updated for "{equipment.name}"'})
        return Response({'error': 'Stock quantity required'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete equipment (admin action)"""
        equipment = self.get_object()
        equipment_name = equipment.name
        equipment.delete()
        return Response(
            {'message': f'Equipment "{equipment_name}" deleted successfully'},
            status=status.HTTP_200_OK
        )

# ===== ORDER MANAGEMENT =====
class AdminOrderManagementViewSet(ModelViewSet):
    """
    Admin Order Management - Monitor and manage all orders
    """
    queryset = Order.objects.all().select_related('buyer').prefetch_related(
        'artwork_items__artwork', 'equipment_items__equipment'
    ).order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order_type', 'status']
    search_fields = ['buyer__username']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def force_complete(self, request, pk=None):
        """Force complete an order (admin action)"""
        order = self.get_object()
        order.status = 'delivered'
        order.save()
        return Response({'message': f'Order #{order.id} marked as delivered'})

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel an order (admin action)"""
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        return Response({'message': f'Order #{order.id} cancelled by admin'})

# ===== ANALYTICS & REPORTS =====
@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def admin_dashboard_stats(request):
    """
    Comprehensive admin dashboard statistics
    """
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # User stats
    user_stats = {
        'total_users': CustomUser.objects.count(),
        'new_users_today': CustomUser.objects.filter(created_at__date=today).count(),
        'new_users_week': CustomUser.objects.filter(created_at__date__gte=week_ago).count(),
        'new_users_month': CustomUser.objects.filter(created_at__date__gte=month_ago).count(),
        'verified_users': CustomUser.objects.filter(is_verified=True).count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'artists': CustomUser.objects.filter(user_type='artist').count(),
        'buyers': CustomUser.objects.filter(user_type='buyer').count(),
    }

    # Content stats
    content_stats = {
        'total_artworks': Artwork.objects.count(),
        'featured_artworks': Artwork.objects.filter(is_featured=True).count(),
        'pending_artworks': 0,  # No longer using AI review
        'total_jobs': Job.objects.count(),
        'open_jobs': Job.objects.filter(status='open').count(),
        'completed_jobs': Job.objects.filter(status='completed').count(),
        'total_categories': Category.objects.count(),
        'active_categories': Category.objects.filter(is_active=True).count(),
    }

    # Financial stats
    financial_stats = {
        'total_revenue': Payment.objects.filter(status='completed').aggregate(
            Sum('amount')
        )['amount__sum'] or 0,
        'revenue_today': Payment.objects.filter(
            status='completed', created_at__date=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'revenue_week': Payment.objects.filter(
            status='completed', created_at__date__gte=week_ago
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'revenue_month': Payment.objects.filter(
            status='completed', created_at__date__gte=month_ago
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_payments': Payment.objects.count(),
        'completed_payments': Payment.objects.filter(status='completed').count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'completed_orders': Order.objects.filter(status='delivered').count(),
    }

    # Activity stats
    activity_stats = {
        'total_bids': Bid.objects.count(),
        'pending_bids': Bid.objects.filter(status='pending').count(),
        'total_messages': Message.objects.count(),
        'unread_messages': Message.objects.filter(is_read=False).count(),
        'total_reviews': Review.objects.count(),
        'average_rating': Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_contracts': Contract.objects.count(),
        'active_contracts': Contract.objects.filter(status='active').count(),
    }

    # Recent activity
    recent_activity = {
        'recent_users': list(
            CustomUser.objects.order_by('-created_at')[:10].values(
                'id', 'username', 'email', 'user_type', 'created_at'
            )
        ),
        'recent_artworks': list(
            Artwork.objects.select_related('artist').order_by('-created_at')[:10].values(
                'id', 'title', 'artist__username', 'price', 'created_at'
            )
        ),
        'recent_jobs': list(
            Job.objects.select_related('buyer').order_by('-created_at')[:10].values(
                'id', 'title', 'buyer__username', 'status', 'created_at'
            )
        ),
        'recent_payments': list(
            Payment.objects.select_related('payer', 'payee').order_by('-created_at')[:10].values(
                'id', 'transaction_id', 'payer__username', 'payee__username', 
                'amount', 'status', 'created_at'
            )
        ),
    }

    return Response({
        'user_stats': user_stats,
        'content_stats': content_stats,
        'financial_stats': financial_stats,
        'activity_stats': activity_stats,
        'recent_activity': recent_activity,
        'generated_at': timezone.now(),
    })

@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def admin_revenue_report(request):
    """
    Detailed revenue report for admin
    """
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()

    # Revenue by payment method
    revenue_by_method = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Daily revenue
    daily_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('day')

    # Top earning artists
    top_artists = Payment.objects.filter(
        status='completed',
        payee__isnull=False,
        created_at__date__range=[start_date, end_date]
    ).values('payee__username').annotate(
        total_earned=Sum('amount'),
        payment_count=Count('id')
    ).order_by('-total_earned')[:10]

    # Top spending buyers
    top_buyers = Payment.objects.filter(
        status='completed',
        created_at__date__range=[start_date, end_date]
    ).values('payer__username').annotate(
        total_spent=Sum('amount'),
        payment_count=Count('id')
    ).order_by('-total_spent')[:10]

    return Response({
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'revenue_by_method': list(revenue_by_method),
        'daily_revenue': list(daily_revenue),
        'top_artists': list(top_artists),
        'top_buyers': list(top_buyers),
        'total_revenue': Payment.objects.filter(
            status='completed',
            created_at__date__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_transactions': Payment.objects.filter(
            status='completed',
            created_at__date__range=[start_date, end_date]
        ).count(),
    })

@api_view(['POST'])
@permission_classes([IsAdminOrStaff])
def bulk_user_action(request):
    """
    Bulk actions on users (verify, activate, deactivate, etc.)
    """
    user_ids = request.data.get('user_ids', [])
    action = request.data.get('action')
    
    if not user_ids or not action:
        return Response({'error': 'User IDs and action required'}, status=status.HTTP_400_BAD_REQUEST)
    
    users = CustomUser.objects.filter(id__in=user_ids)
    count = users.count()
    
    if action == 'verify':
        users.update(is_verified=True)
        message = f'{count} users verified'
    elif action == 'unverify':
        users.update(is_verified=False)
        message = f'{count} users unverified'
    elif action == 'activate':
        users.update(is_active=True)
        message = f'{count} users activated'
    elif action == 'deactivate':
        users.update(is_active=False)
        message = f'{count} users deactivated'
    elif action == 'make_staff':
        users.update(is_staff=True)
        message = f'{count} users made staff'
    elif action == 'remove_staff':
        users.update(is_staff=False)
        message = f'Staff privileges removed from {count} users'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message, 'affected_users': count})

@api_view(['POST'])
@permission_classes([IsAdminOrStaff])
def bulk_artwork_action(request):
    """
    Bulk actions on artworks (feature, approve, reject, etc.)
    """
    artwork_ids = request.data.get('artwork_ids', [])
    action = request.data.get('action')
    
    if not artwork_ids or not action:
        return Response({'error': 'Artwork IDs and action required'}, status=status.HTTP_400_BAD_REQUEST)
    
    artworks = Artwork.objects.filter(id__in=artwork_ids)
    count = artworks.count()
    
    if action == 'feature':
        artworks.update(is_featured=True)
        message = f'{count} artworks featured'
    elif action == 'unfeature':
        artworks.update(is_featured=False)
        message = f'{count} artworks unfeatured'
    elif action == 'approve':
        artworks.update(is_available=True)
        message = f'{count} artworks approved'
    elif action == 'reject':
        artworks.update(is_available=False)
        message = f'{count} artworks rejected'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': message, 'affected_artworks': count})