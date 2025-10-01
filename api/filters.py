# filters.py - Complete Custom Filters using django-filter
from django_filters import rest_framework as filters
from django.db.models import Q, Count, Avg, Sum
from decimal import Decimal
from .models import *


class ArtworkFilter(filters.FilterSet):
    """
    Custom filter for Artwork model with advanced filtering options
    """
    # Price range filters
    min_price = filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        label='Minimum Price'
    )
    max_price = filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        label='Maximum Price'
    )
    
    # Artist filters
    artist_username = filters.CharFilter(
        field_name='artist__username', 
        lookup_expr='icontains',
        label='Artist Username'
    )
    artist_id = filters.NumberFilter(
        field_name='artist__id',
        label='Artist ID'
    )
    
    # Category filters
    category_name = filters.CharFilter(
        field_name='category__name', 
        lookup_expr='icontains',
        label='Category Name'
    )
    
    # Boolean filters
    is_featured = filters.BooleanFilter(
        field_name='is_featured',
        label='Is Featured'
    )
    is_available = filters.BooleanFilter(
        field_name='is_available',
        label='Is Available'
    )
    
    # Date range filters
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Views and likes filters
    min_views = filters.NumberFilter(
        field_name='views_count',
        lookup_expr='gte',
        label='Minimum Views'
    )
    min_likes = filters.NumberFilter(
        field_name='likes_count',
        lookup_expr='gte',
        label='Minimum Likes'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Artwork
        fields = ['artwork_type', 'category', 'is_available', 'is_featured']
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(artist__username__icontains=value) |
            Q(artist__first_name__icontains=value) |
            Q(artist__last_name__icontains=value)
        )


class JobFilter(filters.FilterSet):
    """
    Custom filter for Job model with budget and deadline filtering
    """
    # Budget range filters
    min_budget = filters.NumberFilter(
        field_name='budget_min', 
        lookup_expr='gte',
        label='Minimum Budget'
    )
    max_budget = filters.NumberFilter(
        field_name='budget_max', 
        lookup_expr='lte',
        label='Maximum Budget'
    )
    
    # Buyer filters
    buyer_username = filters.CharFilter(
        field_name='buyer__username', 
        lookup_expr='icontains',
        label='Buyer Username'
    )
    buyer_id = filters.NumberFilter(
        field_name='buyer__id',
        label='Buyer ID'
    )
    
    # Category filters
    category_name = filters.CharFilter(
        field_name='category__name', 
        lookup_expr='icontains',
        label='Category Name'
    )
    
    # Deadline filters
    deadline_after = filters.DateTimeFilter(
        field_name='deadline', 
        lookup_expr='gte',
        label='Deadline After'
    )
    deadline_before = filters.DateTimeFilter(
        field_name='deadline', 
        lookup_expr='lte',
        label='Deadline Before'
    )
    
    # Date created filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Custom filters
    has_bids = filters.BooleanFilter(
        method='filter_has_bids',
        label='Has Bids'
    )
    
    # Duration filter
    max_duration = filters.NumberFilter(
        field_name='duration_days',
        lookup_expr='lte',
        label='Maximum Duration (days)'
    )
    min_duration = filters.NumberFilter(
        field_name='duration_days',
        lookup_expr='gte',
        label='Minimum Duration (days)'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Job
        fields = ['status', 'experience_level', 'category']
    
    def filter_has_bids(self, queryset, name, value):
        """Filter jobs that have or don't have bids"""
        if value:
            return queryset.annotate(bid_count=Count('bids')).filter(bid_count__gt=0)
        return queryset.annotate(bid_count=Count('bids')).filter(bid_count=0)
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(required_skills__icontains=value) |
            Q(buyer__username__icontains=value)
        )


class BidFilter(filters.FilterSet):
    """
    Custom filter for Bid model
    """
    # Amount range filters
    min_amount = filters.NumberFilter(
        field_name='bid_amount', 
        lookup_expr='gte',
        label='Minimum Bid Amount'
    )
    max_amount = filters.NumberFilter(
        field_name='bid_amount', 
        lookup_expr='lte',
        label='Maximum Bid Amount'
    )
    
    # Artist filters
    artist_username = filters.CharFilter(
        field_name='artist__username', 
        lookup_expr='icontains',
        label='Artist Username'
    )
    artist_id = filters.NumberFilter(
        field_name='artist__id',
        label='Artist ID'
    )
    
    # Job filters
    job_title = filters.CharFilter(
        field_name='job__title', 
        lookup_expr='icontains',
        label='Job Title'
    )
    job_id = filters.NumberFilter(
        field_name='job__id',
        label='Job ID'
    )
    job_status = filters.CharFilter(
        field_name='job__status',
        label='Job Status'
    )
    
    # Delivery time filter
    max_delivery_time = filters.NumberFilter(
        field_name='delivery_time',
        lookup_expr='lte',
        label='Maximum Delivery Time'
    )
    min_delivery_time = filters.NumberFilter(
        field_name='delivery_time',
        lookup_expr='gte',
        label='Minimum Delivery Time'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Bid
        fields = ['status']
    
    def filter_search(self, queryset, name, value):
        """Search in cover letter and job title"""
        return queryset.filter(
            Q(cover_letter__icontains=value) |
            Q(job__title__icontains=value) |
            Q(artist__username__icontains=value)
        )


class EquipmentFilter(filters.FilterSet):
    """
    Custom filter for Equipment model
    """
    # Price range filters
    min_price = filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        label='Minimum Price'
    )
    max_price = filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        label='Maximum Price'
    )
    
    # Stock filters
    min_stock = filters.NumberFilter(
        field_name='stock_quantity',
        lookup_expr='gte',
        label='Minimum Stock'
    )
    max_stock = filters.NumberFilter(
        field_name='stock_quantity',
        lookup_expr='lte',
        label='Maximum Stock'
    )
    in_stock = filters.BooleanFilter(
        method='filter_in_stock',
        label='In Stock'
    )
    
    # Date filter
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Equipment
        fields = ['equipment_type', 'is_available']
    
    def filter_in_stock(self, queryset, name, value):
        """Filter equipment that is in stock"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(equipment_type__icontains=value)
        )


class OrderFilter(filters.FilterSet):
    """
    Custom filter for Order model
    """
    # Amount range filters
    min_amount = filters.NumberFilter(
        field_name='total_amount', 
        lookup_expr='gte',
        label='Minimum Amount'
    )
    max_amount = filters.NumberFilter(
        field_name='total_amount', 
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    # Date range filters
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Updated date filters
    updated_after = filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        label='Updated After'
    )
    updated_before = filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        label='Updated Before'
    )
    
    # Buyer filter
    buyer_username = filters.CharFilter(
        field_name='buyer__username',
        lookup_expr='icontains',
        label='Buyer Username'
    )
    buyer_id = filters.NumberFilter(
        field_name='buyer__id',
        label='Buyer ID'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Order
        fields = ['order_type', 'status']
    
    def filter_search(self, queryset, name, value):
        """Search in shipping address and buyer info"""
        return queryset.filter(
            Q(shipping_address__icontains=value) |
            Q(buyer__username__icontains=value) |
            Q(buyer__email__icontains=value)
        )


class PaymentFilter(filters.FilterSet):
    """
    Custom filter for Payment model
    """
    # Amount range filters
    min_amount = filters.NumberFilter(
        field_name='amount', 
        lookup_expr='gte',
        label='Minimum Amount'
    )
    max_amount = filters.NumberFilter(
        field_name='amount', 
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created Before'
    )
    
    # User filters
    payer_username = filters.CharFilter(
        field_name='payer__username', 
        lookup_expr='icontains',
        label='Payer Username'
    )
    payee_username = filters.CharFilter(
        field_name='payee__username', 
        lookup_expr='icontains',
        label='Payee Username'
    )
    payer_id = filters.NumberFilter(
        field_name='payer__id',
        label='Payer ID'
    )
    payee_id = filters.NumberFilter(
        field_name='payee__id',
        label='Payee ID'
    )
    
    # Transaction filter
    transaction_id = filters.CharFilter(
        field_name='transaction_id',
        lookup_expr='icontains',
        label='Transaction ID'
    )
    
    # Related filters
    order_id = filters.NumberFilter(
        field_name='order__id',
        label='Order ID'
    )
    job_id = filters.NumberFilter(
        field_name='job__id',
        label='Job ID'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Payment
        fields = ['payment_method', 'status']
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(transaction_id__icontains=value) |
            Q(payer__username__icontains=value) |
            Q(payee__username__icontains=value)
        )


class MessageFilter(filters.FilterSet):
    """
    Custom filter for Message model
    """
    # User filters
    sender_username = filters.CharFilter(
        field_name='sender__username', 
        lookup_expr='icontains',
        label='Sender Username'
    )
    receiver_username = filters.CharFilter(
        field_name='receiver__username', 
        lookup_expr='icontains',
        label='Receiver Username'
    )
    sender_id = filters.NumberFilter(
        field_name='sender__id',
        label='Sender ID'
    )
    receiver_id = filters.NumberFilter(
        field_name='receiver__id',
        label='Receiver ID'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Job filter
    job_id = filters.NumberFilter(
        field_name='job__id',
        label='Job ID'
    )
    
    # Has attachment filter
    has_attachment = filters.BooleanFilter(
        method='filter_has_attachment',
        label='Has Attachment'
    )
    
    # Content search
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Message
        fields = ['is_read', 'job']
    
    def filter_has_attachment(self, queryset, name, value):
        """Filter messages with or without attachments"""
        if value:
            return queryset.exclude(attachment='')
        return queryset.filter(attachment='')
    
    def filter_search(self, queryset, name, value):
        """Search in message content"""
        return queryset.filter(
            Q(content__icontains=value) |
            Q(sender__username__icontains=value) |
            Q(receiver__username__icontains=value)
        )


class ReviewFilter(filters.FilterSet):
    """
    Custom filter for Review model
    """
    # User filters
    reviewer_username = filters.CharFilter(
        field_name='reviewer__username', 
        lookup_expr='icontains',
        label='Reviewer Username'
    )
    artist_username = filters.CharFilter(
        field_name='artist__username', 
        lookup_expr='icontains',
        label='Artist Username'
    )
    reviewer_id = filters.NumberFilter(
        field_name='reviewer__id',
        label='Reviewer ID'
    )
    artist_id = filters.NumberFilter(
        field_name='artist__id',
        label='Artist ID'
    )
    
    # Rating filters
    min_rating = filters.NumberFilter(
        field_name='rating', 
        lookup_expr='gte',
        label='Minimum Rating'
    )
    max_rating = filters.NumberFilter(
        field_name='rating', 
        lookup_expr='lte',
        label='Maximum Rating'
    )
    rating_exact = filters.NumberFilter(
        field_name='rating',
        label='Exact Rating'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Job filter
    job_id = filters.NumberFilter(
        field_name='job__id',
        label='Job ID'
    )
    job_status = filters.CharFilter(
        field_name='job__status',
        label='Job Status'
    )
    
    # Has comment filter
    has_comment = filters.BooleanFilter(
        method='filter_has_comment',
        label='Has Comment'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Review
        fields = ['rating']
    
    def filter_has_comment(self, queryset, name, value):
        """Filter reviews with or without comments"""
        if value:
            return queryset.exclude(comment='')
        return queryset.filter(comment='')
    
    def filter_search(self, queryset, name, value):
        """Search in review comments"""
        return queryset.filter(
            Q(comment__icontains=value) |
            Q(reviewer__username__icontains=value) |
            Q(artist__username__icontains=value)
        )


class ArtistProfileFilter(filters.FilterSet):
    """
    Custom filter for Artist Profile
    """
    # Hourly rate filters
    min_hourly_rate = filters.NumberFilter(
        field_name='hourly_rate', 
        lookup_expr='gte',
        label='Minimum Hourly Rate'
    )
    max_hourly_rate = filters.NumberFilter(
        field_name='hourly_rate', 
        lookup_expr='lte',
        label='Maximum Hourly Rate'
    )
    
    # Rating filters
    min_rating = filters.NumberFilter(
        field_name='rating', 
        lookup_expr='gte',
        label='Minimum Rating'
    )
    max_rating = filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='Maximum Rating'
    )
    
    # Projects completed filters
    min_projects = filters.NumberFilter(
        field_name='total_projects_completed',
        lookup_expr='gte',
        label='Minimum Projects Completed'
    )
    max_projects = filters.NumberFilter(
        field_name='total_projects_completed',
        lookup_expr='lte',
        label='Maximum Projects Completed'
    )
    
    # Earnings filters
    min_earnings = filters.NumberFilter(
        field_name='total_earnings',
        lookup_expr='gte',
        label='Minimum Total Earnings'
    )
    max_earnings = filters.NumberFilter(
        field_name='total_earnings',
        lookup_expr='lte',
        label='Maximum Total Earnings'
    )
    
    # User filters
    username = filters.CharFilter(
        field_name='user__username', 
        lookup_expr='icontains',
        label='Username'
    )
    user_id = filters.NumberFilter(
        field_name='user__id',
        label='User ID'
    )
    email = filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains',
        label='Email'
    )
    
    # Skills filter
    skills_contain = filters.CharFilter(
        field_name='skills', 
        lookup_expr='icontains',
        label='Skills Contain'
    )
    
    # Verification filter
    is_verified = filters.BooleanFilter(
        field_name='user__is_verified',
        label='Is Verified'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = ArtistProfile
        fields = ['experience_level', 'is_available']
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(skills__icontains=value) |
            Q(bio__icontains=value) |
            Q(portfolio_description__icontains=value)
        )


class BuyerProfileFilter(filters.FilterSet):
    """
    Custom filter for Buyer Profile
    """
    # Spending filters
    min_spent = filters.NumberFilter(
        field_name='total_spent',
        lookup_expr='gte',
        label='Minimum Total Spent'
    )
    max_spent = filters.NumberFilter(
        field_name='total_spent',
        lookup_expr='lte',
        label='Maximum Total Spent'
    )
    
    # Projects posted filter
    min_projects = filters.NumberFilter(
        field_name='projects_posted',
        lookup_expr='gte',
        label='Minimum Projects Posted'
    )
    max_projects = filters.NumberFilter(
        field_name='projects_posted',
        lookup_expr='lte',
        label='Maximum Projects Posted'
    )
    
    # User filters
    username = filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains',
        label='Username'
    )
    user_id = filters.NumberFilter(
        field_name='user__id',
        label='User ID'
    )
    email = filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains',
        label='Email'
    )
    company_name = filters.CharFilter(
        field_name='company_name',
        lookup_expr='icontains',
        label='Company Name'
    )
    
    # Verification filter
    is_verified = filters.BooleanFilter(
        field_name='user__is_verified',
        label='Is Verified'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = BuyerProfile
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(company_name__icontains=value) |
            Q(address__icontains=value)
        )


class ContractFilter(filters.FilterSet):
    """
    Custom filter for Contract model
    """
    # Amount filters
    min_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Minimum Amount'
    )
    max_amount = filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    deadline_after = filters.DateTimeFilter(
        field_name='deadline',
        lookup_expr='gte',
        label='Deadline After'
    )
    deadline_before = filters.DateTimeFilter(
        field_name='deadline',
        lookup_expr='lte',
        label='Deadline Before'
    )
    
    # Signed date filters
    artist_signed_after = filters.DateTimeFilter(
        field_name='artist_signed_at',
        lookup_expr='gte',
        label='Artist Signed After'
    )
    buyer_signed_after = filters.DateTimeFilter(
        field_name='buyer_signed_at',
        lookup_expr='gte',
        label='Buyer Signed After'
    )
    
    # User filters
    artist_id = filters.NumberFilter(
        field_name='artist__id',
        label='Artist ID'
    )
    buyer_id = filters.NumberFilter(
        field_name='buyer__id',
        label='Buyer ID'
    )
    artist_username = filters.CharFilter(
        field_name='artist__username',
        lookup_expr='icontains',
        label='Artist Username'
    )
    buyer_username = filters.CharFilter(
        field_name='buyer__username',
        lookup_expr='icontains',
        label='Buyer Username'
    )
    job_id = filters.NumberFilter(
        field_name='job__id',
        label='Job ID'
    )
    
    # Signed status filters
    is_fully_signed = filters.BooleanFilter(
        method='filter_fully_signed',
        label='Is Fully Signed'
    )
    artist_signed = filters.BooleanFilter(
        field_name='artist_signed',
        label='Artist Signed'
    )
    buyer_signed = filters.BooleanFilter(
        field_name='buyer_signed',
        label='Buyer Signed'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Contract
        fields = ['status', 'rights_type']
    
    def filter_fully_signed(self, queryset, name, value):
        """Filter contracts that are fully signed"""
        if value:
            return queryset.filter(artist_signed=True, buyer_signed=True)
        return queryset.filter(Q(artist_signed=False) | Q(buyer_signed=False))
    
    def filter_search(self, queryset, name, value):
        """Search in contract terms"""
        return queryset.filter(
            Q(terms__icontains=value) |
            Q(artist__username__icontains=value) |
            Q(buyer__username__icontains=value) |
            Q(job__title__icontains=value)
        )


class NotificationFilter(filters.FilterSet):
    """
    Custom filter for Notification model
    """
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Recipient filter
    recipient_id = filters.NumberFilter(
        field_name='recipient__id',
        label='Recipient ID'
    )
    recipient_username = filters.CharFilter(
        field_name='recipient__username',
        lookup_expr='icontains',
        label='Recipient Username'
    )
    
    # Read status
    is_read = filters.BooleanFilter(
        field_name='is_read',
        label='Is Read'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Notification
        fields = ['notification_type', 'is_read']
    
    def filter_search(self, queryset, name, value):
        """Search in notification title and message"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(message__icontains=value) |
            Q(recipient__username__icontains=value)
        )


class CategoryFilter(filters.FilterSet):
    """
    Custom filter for Category model
    """
    # Name filter
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name'
    )
    
    # Active status
    is_active = filters.BooleanFilter(
        field_name='is_active',
        label='Is Active'
    )
    
    # Date filter
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Popularity filter
    min_artworks = filters.NumberFilter(
        method='filter_min_artworks',
        label='Minimum Artworks'
    )
    min_jobs = filters.NumberFilter(
        method='filter_min_jobs',
        label='Minimum Jobs'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = Category
        fields = ['is_active']
    
    def filter_min_artworks(self, queryset, name, value):
        """Filter categories with minimum number of artworks"""
        return queryset.annotate(
            artwork_count=Count('artwork')
        ).filter(artwork_count__gte=value)
    
    def filter_min_jobs(self, queryset, name, value):
        """Filter categories with minimum number of jobs"""
        return queryset.annotate(
            job_count=Count('job')
        ).filter(job_count__gte=value)
    
    def filter_search(self, queryset, name, value):
        """Search in category name and description"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class PlatformAnalyticsFilter(filters.FilterSet):
    """
    Custom filter for Platform Analytics model
    """
    # Date range filters
    date_after = filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='Date After'
    )
    date_before = filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='Date Before'
    )
    date_exact = filters.DateFilter(
        field_name='date',
        label='Exact Date'
    )
    
    # User count filters
    min_total_users = filters.NumberFilter(
        field_name='total_users',
        lookup_expr='gte',
        label='Minimum Total Users'
    )
    min_artists = filters.NumberFilter(
        field_name='total_artists',
        lookup_expr='gte',
        label='Minimum Total Artists'
    )
    min_buyers = filters.NumberFilter(
        field_name='total_buyers',
        lookup_expr='gte',
        label='Minimum Total Buyers'
    )
    
    # Job count filters
    min_jobs_posted = filters.NumberFilter(
        field_name='total_jobs_posted',
        lookup_expr='gte',
        label='Minimum Jobs Posted'
    )
    min_jobs_completed = filters.NumberFilter(
        field_name='total_jobs_completed',
        lookup_expr='gte',
        label='Minimum Jobs Completed'
    )
    
    # Revenue filters
    min_revenue = filters.NumberFilter(
        field_name='total_revenue',
        lookup_expr='gte',
        label='Minimum Total Revenue'
    )
    max_revenue = filters.NumberFilter(
        field_name='total_revenue',
        lookup_expr='lte',
        label='Maximum Total Revenue'
    )
    
    # Platform fees filter
    min_platform_fees = filters.NumberFilter(
        field_name='total_platform_fees',
        lookup_expr='gte',
        label='Minimum Platform Fees'
    )
    
    # Artwork count filter
    min_artworks = filters.NumberFilter(
        field_name='total_artworks_uploaded',
        lookup_expr='gte',
        label='Minimum Artworks Uploaded'
    )
    
    class Meta:
        model = PlatformAnalytics
        fields = ['date']


class CustomUserFilter(filters.FilterSet):
    """
    Custom filter for CustomUser model
    """
    # Username and email filters
    username = filters.CharFilter(
        field_name='username',
        lookup_expr='icontains',
        label='Username'
    )
    email = filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email'
    )
    
    # Name filters
    first_name = filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        label='First Name'
    )
    last_name = filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains',
        label='Last Name'
    )
    
    # Phone filter
    phone_number = filters.CharFilter(
        field_name='phone_number',
        lookup_expr='icontains',
        label='Phone Number'
    )
    
    # Status filters
    is_verified = filters.BooleanFilter(
        field_name='is_verified',
        label='Is Verified'
    )
    is_active = filters.BooleanFilter(
        field_name='is_active',
        label='Is Active'
    )
    is_staff = filters.BooleanFilter(
        field_name='is_staff',
        label='Is Staff'
    )
    
    # Date filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Search filter
    search = filters.CharFilter(
        method='filter_search',
        label='Search'
    )
    
    class Meta:
        model = CustomUser
        fields = ['user_type', 'is_verified', 'is_active']
    
    def filter_search(self, queryset, name, value):
        """Search across multiple user fields"""
        return queryset.filter(
            Q(username__icontains=value) |
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(phone_number__icontains=value)
        )


# Advanced Combined Filters

class AdvancedArtworkFilter(ArtworkFilter):
    """
    Advanced artwork filter with computed fields
    """
    # Popularity filters
    min_engagement = filters.NumberFilter(
        method='filter_min_engagement',
        label='Minimum Engagement (views + likes)'
    )
    
    # Time-based filters
    trending = filters.BooleanFilter(
        method='filter_trending',
        label='Trending (created in last 7 days with high engagement)'
    )
    
    # Artist rating filter
    min_artist_rating = filters.NumberFilter(
        method='filter_min_artist_rating',
        label='Minimum Artist Rating'
    )
    
    def filter_min_engagement(self, queryset, name, value):
        """Filter by total engagement (views + likes)"""
        return queryset.annotate(
            engagement=models.F('views_count') + models.F('likes_count')
        ).filter(engagement__gte=value)
    
    def filter_trending(self, queryset, name, value):
        """Filter trending artworks"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(
                created_at__gte=seven_days_ago
            ).annotate(
                engagement=models.F('views_count') + models.F('likes_count')
            ).filter(engagement__gte=10).order_by('-engagement')
        return queryset
    
    def filter_min_artist_rating(self, queryset, name, value):
        """Filter by minimum artist rating"""
        return queryset.filter(artist__artist_profile__rating__gte=value)


class AdvancedJobFilter(JobFilter):
    """
    Advanced job filter with computed fields
    """
    # Budget-related filters
    budget_range = filters.CharFilter(
        method='filter_budget_range',
        label='Budget Range (low/medium/high)'
    )
    
    # Bid-related filters
    min_bids = filters.NumberFilter(
        method='filter_min_bids',
        label='Minimum Number of Bids'
    )
    max_bids = filters.NumberFilter(
        method='filter_max_bids',
        label='Maximum Number of Bids'
    )
    
    # Urgency filter
    urgent = filters.BooleanFilter(
        method='filter_urgent',
        label='Urgent (deadline within 3 days)'
    )
    
    # Buyer rating filter
    min_buyer_rating = filters.NumberFilter(
        method='filter_min_buyer_rating',
        label='Minimum Buyer Rating (based on completed projects)'
    )
    
    def filter_budget_range(self, queryset, name, value):
        """Filter by budget range categories"""
        if value.lower() == 'low':
            return queryset.filter(budget_max__lte=500)
        elif value.lower() == 'medium':
            return queryset.filter(budget_min__gte=500, budget_max__lte=2000)
        elif value.lower() == 'high':
            return queryset.filter(budget_min__gte=2000)
        return queryset
    
    def filter_min_bids(self, queryset, name, value):
        """Filter by minimum number of bids"""
        return queryset.annotate(
            bid_count=Count('bids')
        ).filter(bid_count__gte=value)
    
    def filter_max_bids(self, queryset, name, value):
        """Filter by maximum number of bids"""
        return queryset.annotate(
            bid_count=Count('bids')
        ).filter(bid_count__lte=value)
    
    def filter_urgent(self, queryset, name, value):
        """Filter urgent jobs (deadline within 3 days)"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            three_days_later = timezone.now() + timedelta(days=3)
            return queryset.filter(
                deadline__lte=three_days_later,
                deadline__gte=timezone.now(),
                status='open'
            )
        return queryset
    
    def filter_min_buyer_rating(self, queryset, name, value):
        """Filter by minimum buyer rating"""
        # Calculate buyer rating based on reviews received
        return queryset.annotate(
            avg_rating=Avg('buyer__posted_jobs__reviews__rating')
        ).filter(avg_rating__gte=value)


class AdvancedArtistProfileFilter(ArtistProfileFilter):
    """
    Advanced artist profile filter with computed metrics
    """
    # Success rate filter
    min_success_rate = filters.NumberFilter(
        method='filter_min_success_rate',
        label='Minimum Success Rate (%)'
    )
    
    # Response rate filter
    active_recently = filters.BooleanFilter(
        method='filter_active_recently',
        label='Active Recently (last 30 days)'
    )
    
    # Top rated filter
    top_rated = filters.BooleanFilter(
        method='filter_top_rated',
        label='Top Rated (rating >= 4.5)'
    )
    
    # Earning range filter
    earning_range = filters.CharFilter(
        method='filter_earning_range',
        label='Earning Range (starter/established/expert)'
    )
    
    def filter_min_success_rate(self, queryset, name, value):
        """Filter by minimum success rate"""
        return queryset.annotate(
            total_jobs=Count('user__hired_projects'),
            completed_jobs=Count('user__hired_projects', filter=Q(user__hired_projects__status='completed'))
        ).filter(
            total_jobs__gt=0
        ).annotate(
            success_rate=(models.F('completed_jobs') * 100.0 / models.F('total_jobs'))
        ).filter(success_rate__gte=value)
    
    def filter_active_recently(self, queryset, name, value):
        """Filter artists active in last 30 days"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            # Check if user has created artworks, bids, or messages recently
            return queryset.filter(
                Q(user__artworks__created_at__gte=thirty_days_ago) |
                Q(user__my_bids__created_at__gte=thirty_days_ago) |
                Q(user__sent_messages__created_at__gte=thirty_days_ago)
            ).distinct()
        return queryset
    
    def filter_top_rated(self, queryset, name, value):
        """Filter top-rated artists"""
        if value:
            return queryset.filter(
                rating__gte=4.5,
                total_projects_completed__gte=5
            )
        return queryset
    
    def filter_earning_range(self, queryset, name, value):
        """Filter by earning range"""
        if value.lower() == 'starter':
            return queryset.filter(total_earnings__lt=1000)
        elif value.lower() == 'established':
            return queryset.filter(total_earnings__gte=1000, total_earnings__lt=10000)
        elif value.lower() == 'expert':
            return queryset.filter(total_earnings__gte=10000)
        return queryset


# Utility filter for date ranges

class DateRangeFilter(filters.FilterSet):
    """
    Reusable date range filter
    """
    date_range = filters.CharFilter(
        method='filter_date_range',
        label='Date Range (today/week/month/year)'
    )
    
    def filter_date_range(self, queryset, name, value):
        """Filter by common date ranges"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if value.lower() == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=start_date)
        elif value.lower() == 'week':
            start_date = now - timedelta(days=7)
            return queryset.filter(created_at__gte=start_date)
        elif value.lower() == 'month':
            start_date = now - timedelta(days=30)
            return queryset.filter(created_at__gte=start_date)
        elif value.lower() == 'year':
            start_date = now - timedelta(days=365)
            return queryset.filter(created_at__gte=start_date)
        
        return queryset


# Export all filters for easy import
__all__ = [
    'ArtworkFilter',
    'JobFilter',
    'BidFilter',
    'EquipmentFilter',
    'OrderFilter',
    'PaymentFilter',
    'MessageFilter',
    'ReviewFilter',
    'ArtistProfileFilter',
    'BuyerProfileFilter',
    'ContractFilter',
    'NotificationFilter',
    'CategoryFilter',
    'PlatformAnalyticsFilter',
    'CustomUserFilter',
    'AdvancedArtworkFilter',
    'AdvancedJobFilter',
    'AdvancedArtistProfileFilter',
    'DateRangeFilter',
]