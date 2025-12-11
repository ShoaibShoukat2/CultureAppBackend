# admin_serializers.py - Admin-specific serializers
from rest_framework import serializers
from .models import *
from .serializers import *

class AdminUserSerializer(serializers.ModelSerializer):
    """
    Admin User Serializer with additional fields
    """
    total_artworks = serializers.SerializerMethodField()
    total_jobs_posted = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    total_earned = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'is_verified', 'is_active',
            'is_staff', 'is_superuser', 'profile_image', 'created_at',
            'updated_at', 'last_login', 'total_artworks', 'total_jobs_posted',
            'total_bids', 'total_spent', 'total_earned', 'last_activity'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login']

    def get_total_artworks(self, obj):
        if obj.user_type == 'artist':
            return obj.artworks.count()
        return 0

    def get_total_jobs_posted(self, obj):
        if obj.user_type == 'buyer':
            return obj.posted_jobs.count()
        return 0

    def get_total_bids(self, obj):
        if obj.user_type == 'artist':
            return obj.my_bids.count()
        return 0

    def get_total_spent(self, obj):
        if obj.user_type == 'buyer':
            return obj.buyer_payments.filter(status='completed').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
        return 0

    def get_total_earned(self, obj):
        if obj.user_type == 'artist':
            return obj.artist_payments.filter(status='completed').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
        return 0

    def get_last_activity(self, obj):
        # Get the most recent activity (artwork upload, job post, bid, etc.)
        activities = []
        
        if obj.user_type == 'artist':
            latest_artwork = obj.artworks.order_by('-created_at').first()
            if latest_artwork:
                activities.append(latest_artwork.created_at)
            
            latest_bid = obj.my_bids.order_by('-created_at').first()
            if latest_bid:
                activities.append(latest_bid.created_at)
        
        elif obj.user_type == 'buyer':
            latest_job = obj.posted_jobs.order_by('-created_at').first()
            if latest_job:
                activities.append(latest_job.created_at)
        
        # Messages
        latest_message = obj.sent_messages.order_by('-created_at').first()
        if latest_message:
            activities.append(latest_message.created_at)
        
        return max(activities) if activities else obj.last_login

class AdminArtworkSerializer(serializers.ModelSerializer):
    """
    Admin Artwork Serializer with additional moderation fields
    """
    artist_username = serializers.CharField(source='artist.username', read_only=True)
    artist_email = serializers.CharField(source='artist.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    duplicate_risk = serializers.SerializerMethodField()
    moderation_status = serializers.SerializerMethodField()

    class Meta:
        model = Artwork
        fields = [
            'id', 'title', 'description', 'artist', 'artist_username', 
            'artist_email', 'category', 'category_name', 'artwork_type',
            'price', 'is_available', 'is_featured', 'views_count', 
            'likes_count', 'created_at', 'updated_at', 's3_image_url',
            's3_watermarked_url', 'rekognition_checked', 'rekognition_labels',
            'similarity_score', 'duplicate_risk', 'moderation_status'
        ]

    def get_duplicate_risk(self, obj):
        if obj.similarity_score > 80:
            return 'HIGH'
        elif obj.similarity_score > 60:
            return 'MEDIUM'
        elif obj.similarity_score > 40:
            return 'LOW'
        return 'NONE'

    def get_moderation_status(self, obj):
        if not obj.rekognition_checked:
            return 'PENDING_REVIEW'
        elif obj.is_available:
            return 'APPROVED'
        else:
            return 'REJECTED'

class AdminJobSerializer(serializers.ModelSerializer):
    """
    Admin Job Serializer with additional management fields
    """
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    hired_artist_username = serializers.CharField(source='hired_artist.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_bids = serializers.SerializerMethodField()
    average_bid = serializers.SerializerMethodField()
    days_since_posted = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'buyer', 'buyer_username',
            'buyer_email', 'category', 'category_name', 'budget_min',
            'budget_max', 'duration_days', 'required_skills',
            'experience_level', 'status', 'hired_artist',
            'hired_artist_username', 'final_amount', 'deadline',
            'created_at', 'updated_at', 'total_bids', 'average_bid',
            'days_since_posted', 'days_until_deadline'
        ]

    def get_total_bids(self, obj):
        return obj.bids.count()

    def get_average_bid(self, obj):
        return obj.calculate_average_bid()

    def get_days_since_posted(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days

    def get_days_until_deadline(self, obj):
        if obj.deadline:
            return (obj.deadline.date() - timezone.now().date()).days
        return None

class AdminPaymentSerializer(serializers.ModelSerializer):
    """
    Admin Payment Serializer with additional financial details
    """
    payer_username = serializers.CharField(source='payer.username', read_only=True)
    payee_username = serializers.CharField(source='payee.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    platform_fee = serializers.SerializerMethodField()
    artist_earning = serializers.SerializerMethodField()
    days_since_payment = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'payer', 'payer_username',
            'payee', 'payee_username', 'order', 'job', 'job_title',
            'amount', 'payment_method', 'status', 'hire_status',
            'stripe_payment_intent', 'created_at', 'platform_fee',
            'artist_earning', 'days_since_payment'
        ]

    def get_platform_fee(self, obj):
        return obj.calculate_platform_fee()

    def get_artist_earning(self, obj):
        return obj.calculate_artist_earning()

    def get_days_since_payment(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days

class AdminOrderSerializer(serializers.ModelSerializer):
    """
    Admin Order Serializer with detailed order information
    """
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    artwork_items = serializers.SerializerMethodField()
    equipment_items = serializers.SerializerMethodField()
    days_since_order = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'buyer_username', 'buyer_email',
            'order_type', 'status', 'total_amount', 'shipping_address',
            'created_at', 'updated_at', 'artwork_items', 'equipment_items',
            'days_since_order'
        ]

    def get_artwork_items(self, obj):
        return obj.artwork_items.count()

    def get_equipment_items(self, obj):
        return obj.equipment_items.count()

    def get_days_since_order(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days

class AdminAnalyticsSerializer(serializers.ModelSerializer):
    """
    Admin Analytics Serializer with calculated metrics
    """
    growth_rate = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    average_transaction = serializers.SerializerMethodField()

    class Meta:
        model = PlatformAnalytics
        fields = [
            'id', 'date', 'total_users', 'total_artists', 'total_buyers',
            'total_jobs_posted', 'total_jobs_completed', 'total_artworks_uploaded',
            'total_revenue', 'total_platform_fees', 'growth_rate',
            'conversion_rate', 'average_transaction'
        ]

    def get_growth_rate(self, obj):
        # Calculate user growth rate compared to previous day
        previous_day = obj.date - timedelta(days=1)
        try:
            previous_analytics = PlatformAnalytics.objects.get(date=previous_day)
            if previous_analytics.total_users > 0:
                return ((obj.total_users - previous_analytics.total_users) / previous_analytics.total_users) * 100
        except PlatformAnalytics.DoesNotExist:
            pass
        return 0

    def get_conversion_rate(self, obj):
        # Calculate job completion rate
        if obj.total_jobs_posted > 0:
            return (obj.total_jobs_completed / obj.total_jobs_posted) * 100
        return 0

    def get_average_transaction(self, obj):
        # Calculate average transaction amount
        completed_payments = Payment.objects.filter(
            status='completed',
            created_at__date=obj.date
        )
        if completed_payments.exists():
            return completed_payments.aggregate(models.Avg('amount'))['amount__avg']
        return 0

class AdminNotificationSerializer(serializers.ModelSerializer):
    """
    Admin Notification Serializer for system-wide notifications
    """
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    days_since_created = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_username', 'notification_type',
            'title', 'message', 'is_read', 'created_at', 'days_since_created'
        ]

    def get_days_since_created(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days

class AdminSystemStatsSerializer(serializers.Serializer):
    """
    Serializer for system-wide statistics
    """
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_week = serializers.IntegerField()
    new_users_month = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    artists = serializers.IntegerField()
    buyers = serializers.IntegerField()
    
    total_artworks = serializers.IntegerField()
    featured_artworks = serializers.IntegerField()
    pending_artworks = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    open_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_today = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_week = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payments = serializers.IntegerField()
    
    total_bids = serializers.IntegerField()
    pending_bids = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)

class BulkActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    artwork_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    action = serializers.ChoiceField(choices=[
        ('verify', 'Verify'),
        ('unverify', 'Unverify'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('make_staff', 'Make Staff'),
        ('remove_staff', 'Remove Staff'),
        ('feature', 'Feature'),
        ('unfeature', 'Unfeature'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ])

class AdminRevenueReportSerializer(serializers.Serializer):
    """
    Serializer for revenue reports
    """
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    revenue_by_method = serializers.ListField()
    daily_revenue = serializers.ListField()
    top_artists = serializers.ListField()
    top_buyers = serializers.ListField()