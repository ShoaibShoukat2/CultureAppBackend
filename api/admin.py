from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import (
    CustomUser, ArtistProfile, BuyerProfile, Category, Artwork,
    Job, Bid, Equipment, Order, ArtworkOrderItem, EquipmentOrderItem,
    Payment, Message, Review, Contract, Notification, PlatformAnalytics
)
from .email_service import EmailService

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'user_type', 'is_verified', 'is_active', 'is_staff', 'created_at', 'user_actions')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    list_editable = ('is_verified', 'is_active')
    actions = ['verify_users', 'unverify_users', 'activate_users', 'deactivate_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number')
        }),
        ('User Type & Status', {
            'fields': ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Profile', {
            'fields': ('profile_image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def user_actions(self, obj):
        """Quick action buttons for user management"""
        actions = []
        if not obj.is_verified:
            actions.append(f'<a class="button" href="#" onclick="verifyUser({obj.id})">Verify</a>')
        if not obj.is_active:
            actions.append(f'<a class="button" href="#" onclick="activateUser({obj.id})">Activate</a>')
        else:
            actions.append(f'<a class="button" href="#" onclick="deactivateUser({obj.id})">Deactivate</a>')
        return mark_safe(' '.join(actions))
    user_actions.short_description = 'Quick Actions'
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users verified successfully.')
    verify_users.short_description = "Verify selected users"
    
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} users unverified.')
    unverify_users.short_description = "Unverify selected users"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'experience_level', 'hourly_rate', 'rating', 'total_projects_completed', 'is_available')
    search_fields = ('user__username', 'skills')
    list_filter = ('experience_level', 'is_available')

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'company_name', 'total_spent', 'projects_posted')
    search_fields = ('user__username', 'company_name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'artwork_type', 'category', 'price', 'is_available', 'is_featured', 'views_count', 'moderation_status', 'artwork_actions')
    list_filter = ('artwork_type', 'is_available', 'is_featured', 'category', 'rekognition_checked', 'created_at')
    search_fields = ('title', 'artist__username', 'description')
    readonly_fields = ('views_count', 'likes_count', 'created_at', 'updated_at', 'rekognition_checked', 'similarity_score')
    list_editable = ('is_available', 'is_featured')
    actions = ['feature_artworks', 'unfeature_artworks', 'approve_artworks', 'reject_artworks']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'artist', 'category', 'artwork_type', 'price')
        }),
        ('Status & Visibility', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Images', {
            'fields': ('image', 'watermarked_image', 's3_image_url', 's3_watermarked_url')
        }),
        ('AI & Moderation', {
            'fields': ('rekognition_checked', 'rekognition_labels', 'similarity_score'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def moderation_status(self, obj):
        """Show moderation status with color coding"""
        if not obj.rekognition_checked:
            return format_html('<span style="color: orange;">⏳ Pending Review</span>')
        elif obj.is_available:
            return format_html('<span style="color: green;">✅ Approved</span>')
        else:
            return format_html('<span style="color: red;">❌ Rejected</span>')
    moderation_status.short_description = 'Status'
    
    def artwork_actions(self, obj):
        """Quick action buttons for artwork management"""
        actions = []
        if not obj.is_featured:
            actions.append(f'<a class="button" href="#" onclick="featureArtwork({obj.id})">Feature</a>')
        else:
            actions.append(f'<a class="button" href="#" onclick="unfeatureArtwork({obj.id})">Unfeature</a>')
        
        if not obj.is_available:
            actions.append(f'<a class="button" href="#" onclick="approveArtwork({obj.id})">Approve</a>')
        else:
            actions.append(f'<a class="button" href="#" onclick="rejectArtwork({obj.id})">Reject</a>')
        
        return mark_safe(' '.join(actions))
    artwork_actions.short_description = 'Quick Actions'
    
    def feature_artworks(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} artworks featured successfully.')
    feature_artworks.short_description = "Feature selected artworks"
    
    def unfeature_artworks(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} artworks unfeatured.')
    unfeature_artworks.short_description = "Unfeature selected artworks"
    
    def approve_artworks(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} artworks approved.')
    approve_artworks.short_description = "Approve selected artworks"
    
    def reject_artworks(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} artworks rejected.')
    reject_artworks.short_description = "Reject selected artworks"
    
    def save_model(self, request, obj, form, change):
        # pehle normal save
        super().save_model(request, obj, form, change)
        # apply watermark after image is fully uploaded
        if obj.image:
            obj.apply_watermark()
            obj.save(update_fields=['watermarked_image'])



            

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
    list_display = ('id', 'buyer', 'order_type', 'status', 'total_amount', 'created_at', 'email_actions')
    list_filter = ('order_type', 'status')
    search_fields = ('buyer__username',)
    actions = ['send_order_confirmation_emails', 'send_status_update_emails']
    
    def email_actions(self, obj):
        """Email action buttons"""
        actions = []
        actions.append(f'<a class="button" href="#" onclick="sendOrderEmail({obj.id})">Send Confirmation</a>')
        return mark_safe(' '.join(actions))
    email_actions.short_description = 'Email Actions'
    
    def send_order_confirmation_emails(self, request, queryset):
        """Admin action to manually send order confirmation emails"""
        count = 0
        for order in queryset:
            if EmailService.send_purchase_confirmation(order):
                count += 1
        messages.success(request, f'Successfully sent {count} order confirmation emails.')
    send_order_confirmation_emails.short_description = "Send order confirmation emails"
    
    def send_status_update_emails(self, request, queryset):
        """Admin action to send status update emails"""
        count = 0
        for order in queryset:
            if EmailService.send_order_status_update(order, 'pending', order.status):
                count += 1
        messages.success(request, f'Successfully sent {count} status update emails.')
    send_status_update_emails.short_description = "Send status update emails"
    
    def save_model(self, request, obj, form, change):
        # Track status changes
        if change:
            try:
                old_obj = Order.objects.get(pk=obj.pk)
                if old_obj.status != obj.status:
                    obj._old_status = old_obj.status
            except Order.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

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
    list_display = ('transaction_id', 'payer', 'payee', 'amount', 'payment_method', 'status', 'hire_status', 'created_at', 'payment_actions')
    list_filter = ('payment_method', 'status', 'hire_status', 'created_at')
    search_fields = ('transaction_id', 'payer__username', 'payee__username')
    readonly_fields = ('transaction_id', 'created_at', 'stripe_payment_intent')
    actions = ['refund_payments', 'release_payments', 'send_payment_confirmation_emails']
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('transaction_id', 'payer', 'payee', 'amount', 'payment_method')
        }),
        ('Status', {
            'fields': ('status', 'hire_status')
        }),
        ('Related Objects', {
            'fields': ('order', 'job')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def payment_actions(self, obj):
        """Quick action buttons for payment management"""
        actions = []
        if obj.status == 'completed' and obj.hire_status == 'pending':
            actions.append(f'<a class="button" href="#" onclick="releasePayment({obj.id})">Release</a>')
        if obj.status == 'completed':
            actions.append(f'<a class="button" href="#" onclick="refundPayment({obj.id})">Refund</a>')
        actions.append(f'<a class="button" href="#" onclick="sendPaymentEmail({obj.id})">Send Email</a>')
        return mark_safe(' '.join(actions))
    payment_actions.short_description = 'Quick Actions'
    
    def refund_payments(self, request, queryset):
        updated = queryset.filter(status='completed').update(status='refunded')
        self.message_user(request, f'{updated} payments refunded.')
    refund_payments.short_description = "Refund selected payments"
    
    def release_payments(self, request, queryset):
        updated = queryset.filter(hire_status='pending').update(hire_status='released')
        self.message_user(request, f'{updated} payments released to artists.')
    release_payments.short_description = "Release selected payments"
    
    def send_payment_confirmation_emails(self, request, queryset):
        """Admin action to manually send payment confirmation emails"""
        count = 0
        for payment in queryset:
            if EmailService.send_payment_confirmation(payment):
                count += 1
        messages.success(request, f'Successfully sent {count} payment confirmation emails.')
    send_payment_confirmation_emails.short_description = "Send payment confirmation emails"

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


# Customize admin site
admin.site.site_header = "ArtConnect Admin Dashboard"
admin.site.site_title = "ArtConnect Admin Portal"
admin.site.index_title = "Welcome to ArtConnect Admin - Comprehensive Management System"

# Add custom CSS and JS
class AdminConfig:
    """Custom admin configuration"""
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)





