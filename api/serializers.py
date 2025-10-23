# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import *
from decimal import Decimal

# User Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 
                 'phone_number', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        
        # Create profile based on user type
        if user.user_type == 'artist':
            ArtistProfile.objects.create(user=user)
        elif user.user_type == 'buyer':
            BuyerProfile.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        return attrs
    

    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'is_verified', 'profile_image',
                 'created_at']
        read_only_fields = ['id', 'username', 'user_type', 'is_verified', 'created_at']
        

        
        
        

# Artist Profile Serializers
class ArtistProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    completion_rate = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtistProfile
        fields = ['user', 'bio', 'skills', 'experience_level', 'hourly_rate',
                 'portfolio_description', 'rating', 'total_projects_completed',
                 'total_earnings', 'is_available', 'completion_rate', 'total_reviews']
    
    def get_completion_rate(self, obj):
        return obj.calculate_completion_rate()
    
    def get_total_reviews(self, obj):
        """Count all reviews received by this artist."""
        return Review.objects.filter(job__hired_artist=obj.user).count()

        



class ArtistProfileUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='user.profile_image', required=False)

    class Meta:
        model = ArtistProfile
        fields = [
            'bio',
            'skills',
            'experience_level',
            'hourly_rate',
            'portfolio_description',
            'is_available',
            'profile_image',
        ]

    def update(self, instance, validated_data):
        # Handle nested user data for profile image
        user_data = validated_data.pop('user', {})
        profile_image = user_data.get('profile_image', None)

        # Update artist profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update user profile image if provided
        if profile_image:
            instance.user.profile_image = profile_image
            instance.user.save()

        return instance



        

# Buyer Profile Serializers
class BuyerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = BuyerProfile
        fields = ['user', 'company_name', 'address', 'total_spent', 'projects_posted']
        


class BuyerProfileUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='user.profile_image', required=False)

    class Meta:
        model = BuyerProfile
        fields = ['company_name', 'address', 'profile_image']

    def update(self, instance, validated_data):
        # Extract nested user data (for profile image)
        user_data = validated_data.pop('user', {})
        profile_image = user_data.get('profile_image', None)

        # Update BuyerProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update user's profile image if provided
        if profile_image:
            instance.user.profile_image = profile_image
            instance.user.save()

        return instance


        



# Category Serializers
class CategorySerializer(serializers.ModelSerializer):
    artworks_count = serializers.SerializerMethodField()
    jobs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at',
                 'artworks_count', 'jobs_count']
    
    def get_artworks_count(self, obj):
        return obj.artwork_set.filter(is_available=True).count()
    
    def get_jobs_count(self, obj):
        return obj.job_set.filter(status='open').count()




# Artwork Serializers
class ArtworkSerializer(serializers.ModelSerializer):
    artist = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Artwork
        fields = ['id', 'artist', 'title', 'description', 'category', 'category_id',
                 'artwork_type', 'price', 'image', 'watermarked_image', 'is_available',
                 'is_featured', 'views_count', 'likes_count', 'created_at', 'updated_at']
        read_only_fields = ['artist', 'views_count', 'likes_count', 'watermarked_image']
    
    def create(self, validated_data):
        validated_data['artist'] = self.context['request'].user
        return super().create(validated_data)
  
    

class ArtworkListSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'artist_name', 'category_name', 'artwork_type',
                 'price', 'image', 'is_featured', 'views_count', 'likes_count', 'created_at']
       
       
       
     
        

# Job/Project Serializers
class JobSerializer(serializers.ModelSerializer):
    buyer = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    hired_artist = UserProfileSerializer(read_only=True)
    average_bid = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    deadline_approaching = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'buyer', 'title', 'description', 'category', 'category_id',
                 'budget_min', 'budget_max', 'duration_days', 'required_skills',
                 'experience_level', 'status', 'hired_artist', 'final_amount',
                 'deadline', 'created_at', 'updated_at', 'average_bid', 'total_bids',
                 'deadline_approaching']
        read_only_fields = ['buyer', 'hired_artist', 'final_amount', 'status']
    
    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        return super().create(validated_data)
    
    def get_average_bid(self, obj):
        return obj.calculate_average_bid()
    
    def get_total_bids(self, obj):
        return obj.get_total_bids()
    
    def get_deadline_approaching(self, obj):
        return obj.is_deadline_approaching()



class JobListSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_bids = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'buyer_name', 'category_name', 'budget_min', 
                 'budget_max', 'duration_days', 'experience_level', 'status',
                 'deadline', 'created_at', 'total_bids']
    
    def get_total_bids(self, obj):
        return obj.get_total_bids()

# Bid Serializers
class BidSerializer(serializers.ModelSerializer):
    artist = UserProfileSerializer(read_only=True)
    job = JobListSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)
    bid_rank = serializers.SerializerMethodField()
    
    class Meta:
        model = Bid
        fields = ['id', 'job', 'job_id', 'artist', 'bid_amount', 'delivery_time',
                 'cover_letter', 'status', 'created_at', 'bid_rank']
        read_only_fields = ['artist', 'status', 'bid_rank']
    
    def create(self, validated_data):
        validated_data['artist'] = self.context['request'].user
        return super().create(validated_data)
    
    def get_bid_rank(self, obj):
        return obj.calculate_bid_rank()

class BidListSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = Bid
        fields = ['id', 'job_title', 'artist_name', 'bid_amount', 'delivery_time',
                 'status', 'created_at']

# Equipment Serializers
class EquipmentSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'description', 'equipment_type', 'price',
                 'stock_quantity', 'image', 'is_available', 'created_at', 'in_stock']
    
    def get_in_stock(self, obj):
        return obj.is_in_stock()
    
    


# Order Serializers
class ArtworkOrderItemSerializer(serializers.ModelSerializer):
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    artwork_artist = serializers.CharField(source='artwork.artist.username', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ArtworkOrderItem
        fields = ['id', 'artwork', 'artwork_title', 'artwork_artist', 'quantity',
                 'price', 'total_price']
        read_only_fields = ['price']
    
    def get_total_price(self, obj):
        return obj.get_total_price()

class EquipmentOrderItemSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = EquipmentOrderItem
        fields = ['id', 'equipment', 'equipment_name', 'quantity', 'price', 'total_price']
        read_only_fields = ['price']
    
    def get_total_price(self, obj):
        return obj.get_total_price()

class OrderSerializer(serializers.ModelSerializer):
    buyer = UserProfileSerializer(read_only=True)
    artwork_items = ArtworkOrderItemSerializer(many=True, read_only=True)
    equipment_items = EquipmentOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'order_type', 'status', 'total_amount',
                 'shipping_address', 'created_at', 'updated_at', 'artwork_items',
                 'equipment_items']
        read_only_fields = ['buyer', 'total_amount']
    
    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        return super().create(validated_data)

class OrderCreateSerializer(serializers.Serializer):
    order_type = serializers.ChoiceField(choices=Order.ORDER_TYPES)
    shipping_address = serializers.CharField(max_length=500)
    artwork_items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    equipment_items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    
    def create(self, validated_data):
        request = self.context['request']
        artwork_items_data = validated_data.pop('artwork_items', [])
        equipment_items_data = validated_data.pop('equipment_items', [])
        
        # Create order
        order = Order.objects.create(
            buyer=request.user,
            **validated_data
        )
        
        # Create artwork items
        for item_data in artwork_items_data:
            artwork = Artwork.objects.get(id=item_data['artwork_id'])
            ArtworkOrderItem.objects.create(
                order=order,
                artwork=artwork,
                quantity=item_data.get('quantity', 1),
                price=artwork.price
            )
        
        # Create equipment items
        for item_data in equipment_items_data:
            equipment = Equipment.objects.get(id=item_data['equipment_id'])
            EquipmentOrderItem.objects.create(
                order=order,
                equipment=equipment,
                quantity=item_data.get('quantity', 1),
                price=equipment.price
            )
        
        # Calculate total
        order.calculate_total()
        return order

# Payment Serializers
class PaymentSerializer(serializers.ModelSerializer):
    payer = UserProfileSerializer(read_only=True)
    payee = UserProfileSerializer(read_only=True)
    platform_fee = serializers.SerializerMethodField()
    artist_earning = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'payer', 'payee', 'order', 'job', 'amount', 'payment_method',
                 'status', 'transaction_id', 'created_at', 'platform_fee', 'artist_earning']
        read_only_fields = ['payer', 'transaction_id', 'platform_fee', 'artist_earning']
    
    def get_platform_fee(self, obj):
        return obj.calculate_platform_fee()
    
    def get_artist_earning(self, obj):
        return obj.calculate_artist_earning()

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payee', 'order', 'job', 'amount', 'payment_method']
    
    def create(self, validated_data):
        validated_data['payer'] = self.context['request'].user
        return super().create(validated_data)

# Message Serializers
class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    receiver = UserProfileSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'receiver_id', 'job', 'content',
                 'attachment', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        receiver_id = validated_data.pop('receiver_id')
        validated_data['receiver'] = CustomUser.objects.get(id=receiver_id)
        return super().create(validated_data)

# Review Serializers
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserProfileSerializer(read_only=True)
    artist = UserProfileSerializer(read_only=True)
    job = JobListSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'artist', 'job', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer', 'artist']

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['job', 'rating', 'comment']
    
    def create(self, validated_data):
        job = validated_data['job']
        validated_data['reviewer'] = self.context['request'].user
        validated_data['artist'] = job.hired_artist
        return super().create(validated_data)

# Contract Serializers
class ContractSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    artist = UserProfileSerializer(read_only=True)
    buyer = UserProfileSerializer(read_only=True)
    is_fully_signed = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = ['id', 'job', 'artist', 'buyer', 'terms', 'rights_type',
                 'amount', 'deadline', 'status', 'artist_signed', 'buyer_signed',
                 'artist_signed_at', 'buyer_signed_at', 'created_at', 'is_fully_signed']
    
    def get_is_fully_signed(self, obj):
        return obj.is_fully_signed()

# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at']

# Analytics Serializers
class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformAnalytics
        fields = ['date', 'total_users', 'total_artists', 'total_buyers',
                 'total_jobs_posted', 'total_jobs_completed', 'total_artworks_uploaded',
                 'total_revenue', 'total_platform_fees']
        
        
        




