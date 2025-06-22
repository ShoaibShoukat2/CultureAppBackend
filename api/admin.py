from django.contrib import admin
from .models import (
    CustomUser, ArtistProfile, BuyerProfile, Category, Artwork,
    Job, Bid, Equipment, Order, ArtworkOrderItem, EquipmentOrderItem,
    Payment, Message, Review, Contract, Notification, PlatformAnalytics
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')

@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_level', 'hourly_rate', 'rating', 'total_projects_completed', 'is_available')
    search_fields = ('user__username', 'skills')
    list_filter = ('experience_level', 'is_available')

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'total_spent', 'projects_posted')
    search_fields = ('user__username', 'company_name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'artwork_type', 'category', 'price', 'is_available', 'is_featured', 'views_count')
    list_filter = ('artwork_type', 'is_available', 'is_featured', 'category')
    search_fields = ('title', 'artist__username', 'description')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'buyer', 'category', 'experience_level', 'status', 'budget_min', 'budget_max', 'deadline')
    list_filter = ('status', 'experience_level', 'category')
    search_fields = ('title', 'buyer__username', 'required_skills')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('job', 'artist', 'bid_amount', 'delivery_time', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('job__title', 'artist__username')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'price', 'stock_quantity', 'is_available')
    list_filter = ('equipment_type', 'is_available')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'order_type', 'status', 'total_amount', 'created_at')
    list_filter = ('order_type', 'status')
    search_fields = ('buyer__username',)

@admin.register(ArtworkOrderItem)
class ArtworkOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'artwork', 'quantity', 'price')
    search_fields = ('artwork__title', 'order__id')

@admin.register(EquipmentOrderItem)
class EquipmentOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'equipment', 'quantity', 'price')
    search_fields = ('equipment__name', 'order__id')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payer', 'payee', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('transaction_id', 'payer__username', 'payee__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'job', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'receiver__username', 'content')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'artist', 'job', 'rating', 'created_at')
    search_fields = ('reviewer__username', 'artist__username', 'comment')
    list_filter = ('rating',)

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('job', 'artist', 'buyer', 'amount', 'status', 'is_fully_signed', 'deadline')
    list_filter = ('status', 'rights_type')
    search_fields = ('job__title', 'artist__username', 'buyer__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'title', 'message')

@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'total_users', 'total_artists', 'total_buyers',
        'total_jobs_posted', 'total_jobs_completed',
        'total_artworks_uploaded', 'total_revenue', 'total_platform_fees'
    )
    search_fields = ('date',)
    ordering = ('-date',)


admin.site.site_header = "ArtConnect Admin"
admin.site.site_title = "ArtConnect Portal"
admin.site.index_title = "Welcome to ArtConnect Admin"

