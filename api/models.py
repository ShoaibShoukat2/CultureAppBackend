from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from PIL import Image
import os

# Custom User Model
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('artist', 'Artist'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='buyer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 2FA fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


class TwoFactorSession(models.Model):
    """Temporary session for 2FA verification"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"2FA Session for {self.user.username}"

 

# Artist Profile Model
class ArtistProfile(models.Model):
    SKILL_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='artist_profile')
    bio = models.TextField(max_length=1000, blank=True)
    skills = models.TextField(help_text="Comma-separated skills")
    experience_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    portfolio_description = models.TextField(max_length=2000, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_projects_completed = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    
    
    
    def calculate_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.user.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2)
            self.save()
        return self.rating
    
    def calculate_completion_rate(self):
        """Calculate project completion rate"""
        total_projects = self.user.hired_projects.count()
        completed_projects = self.user.hired_projects.filter(status='completed').count()
        if total_projects > 0:
            return round((completed_projects / total_projects) * 100, 2)
        return 0

    
    def __str__(self):
        return f"{self.user.username} - Artist Profile"








# Buyer Profile Model
class BuyerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(max_length=500, blank=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    projects_posted = models.PositiveIntegerField(default=0)
    
    def calculate_total_spent(self):
        """Calculate total amount spent by buyer"""
        orders = self.user.buyer_orders.filter(status='completed')
        payments = self.user.buyer_payments.filter(status='completed')
        
        order_total = orders.aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        payment_total = payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        self.total_spent = order_total + payment_total
        self.save()
        return self.total_spent
    
    def __str__(self):
        return f"{self.user.username} - Buyer Profile"

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

# Artwork Model
class Artwork(models.Model):
    ARTWORK_TYPES = (
        ('digital', 'Digital Art'),
        ('physical', 'Physical Art'),
        ('mixed', 'Mixed Media'),
    )
    
    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    artwork_type = models.CharField(max_length=20, choices=ARTWORK_TYPES, default='digital')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Image storage fields
    image = models.ImageField(upload_to='artworks/')
    watermarked_image = models.ImageField(upload_to='watermarked_artworks/', blank=True, null=True)
    
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    
    def apply_watermark(self):
        """
        Apply a bold, tiled, diagonal text watermark across the whole image
        so the watermark is clearly visible over the entire picture.
        """
        if not (self.image and (not self.watermarked_image)):
            return

        try:
            original = Image.open(self.image).convert("RGBA")
            txt = "© CultureUp"  # <- change text if you want

            # pick a truetype bold font if available (preferred)
            font_size = max(30, int(original.width * 0.12))  # ~12% of image width
            font = None
            for fpath in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "arial.ttf"):
                try:
                    font = ImageFont.truetype(fpath, font_size)
                    break
                except Exception:
                    font = None
            if font is None:
                # fallback (may be small, but will still work)
                font = ImageFont.load_default()

            # create a single watermark image (text) and rotate it
            # first determine text size
            dummy = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            dummydraw = ImageDraw.Draw(dummy)
            
            try:
                bbox = dummydraw.textbbox((0, 0), txt, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except AttributeError:
                text_w, text_h = dummydraw.textsize(txt, font=font)

            padding = int(font_size * 0.4)
            text_img = Image.new("RGBA", (text_w + padding * 2, text_h + padding * 2), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)

            # draw text with stroke for better visibility
            # stroke_width works on Pillow >= 5.2; fallback draws shadow
            fill_color = (255, 255, 255, 200)   # white with high opacity
            stroke_color = (0, 0, 0, 200)       # black stroke for contrast
            try:
                text_draw.text((padding, padding), txt, font=font,
                            fill=fill_color, stroke_width=2, stroke_fill=stroke_color)
            except TypeError:
                # older Pillow: draw shadow then text
                text_draw.text((padding+2, padding+2), txt, font=font, fill=stroke_color)
                text_draw.text((padding, padding), txt, font=font, fill=fill_color)

            # rotate watermark text image (diagonal)
            angle = -30
            rotated = text_img.rotate(angle, expand=1)

            # create layer to tile watermark
            layer = Image.new("RGBA", original.size, (0, 0, 0, 0))

            # tile the rotated watermark across the layer
            rw, rh = rotated.size
            step_x = int(rw * 0.9)  # overlap a bit so it's continuous
            step_y = int(rh * 0.9)
            # start offsets to center pattern
            start_x = -rw
            start_y = -rh

            for x in range(start_x, original.width + rw, step_x):
                for y in range(start_y, original.height + rh, step_y):
                    layer.paste(rotated, (x, y), rotated)

            # optionally dim the watermark layer overall (if too strong)
            # to make it uniformly semi-transparent multiply alpha
            # choose alpha_factor between 0 (invisible) and 1 (full)
            alpha_factor = 1.0  # 1.0 = full as drawn (we already used high alpha); reduce if too strong
            if alpha_factor < 1.0:
                # apply alpha multiplication
                alpha = layer.split()[3].point(lambda p: int(p * alpha_factor))
                layer.putalpha(alpha)

            # composite the watermark layer on top of original
            combined = Image.alpha_composite(original, layer).convert("RGB")

            # save to memory and to model field
            temp = BytesIO()
            combined.save(temp, format='JPEG', quality=90)
            temp.seek(0)
            file_name = f"watermarked_{self.image.name.split('/')[-1]}"
            self.watermarked_image.save(file_name, ContentFile(temp.read()), save=False)

        except Exception as e:
            # for debugging you can log the exception
            print("Watermarking failed:", e)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.watermarked_image:
            self.apply_watermark()
            super().save(update_fields=['watermarked_image'])

        
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def __str__(self):
        return f"{self.title} by {self.artist.username}"

# Job/Project Model
class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )
    
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=3000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    required_skills = models.TextField(help_text="Comma-separated required skills")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    hired_artist = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='hired_projects'
    )
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_average_bid(self):
        """Calculate average bid amount for this job"""
        bids = self.bids.all()
        if bids.exists():
            avg_bid = bids.aggregate(models.Avg('bid_amount'))['bid_amount__avg']
            return round(avg_bid, 2)
        return 0
    
    def get_total_bids(self):
        """Get total number of bids"""
        return self.bids.count()
    
    def is_deadline_approaching(self, days=3):
        """Check if deadline is approaching within specified days"""
        if self.deadline:
            time_diff = self.deadline - timezone.now()
            return time_diff.days <= days
        return False
    
    def __str__(self):
        return f"{self.title} - {self.buyer.username}"

# Bid Model
class Bid(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bids')
    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in days")
    cover_letter = models.TextField(max_length=1500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['job', 'artist']
    
    def calculate_bid_rank(self):
        """Calculate rank of this bid among all bids for the job"""
        all_bids = self.job.bids.order_by('bid_amount')
        for index, bid in enumerate(all_bids, 1):
            if bid.id == self.id:
                return index
        return 0
    
    def __str__(self):
        return f"Bid by {self.artist.username} for {self.job.title}"
    
    

    

    

# Equipment Model
class Equipment(models.Model):
    EQUIPMENT_TYPES = (
        ('frame', 'Frame'),
        ('paint', 'Paint'),
        ('brush', 'Brush'),
        ('canvas', 'Canvas'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_in_stock(self):
        """Check if equipment is in stock"""
        return self.stock_quantity > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.name} - PKR{self.price}"
    
    
    
    

# Order Model
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    ORDER_TYPES = (
        ('artwork', 'Artwork Purchase'),
        ('equipment', 'Equipment Purchase'),
    )
    
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buyer_orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_address = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        """Calculate total order amount"""
        artwork_total = self.artwork_items.aggregate(
            total=models.Sum(models.F('quantity') * models.F('price'))
        )['total'] or Decimal('0.00')
        
        equipment_total = self.equipment_items.aggregate(
            total=models.Sum(models.F('quantity') * models.F('price'))
        )['total'] or Decimal('0.00')
        
        self.total_amount = artwork_total + equipment_total
        self.save()
        return self.total_amount
    
    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

# Order Item Models
class ArtworkOrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='artwork_items')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.artwork.price
        super().save(*args, **kwargs)
    
    def get_total_price(self):
        return self.quantity * self.price

class EquipmentOrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='equipment_items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.equipment.price
        super().save(*args, **kwargs)
    
    def get_total_price(self):
        return self.quantity * self.price
   

# Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('jazzcash', 'JazzCash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('stripe', 'Stripe'),
        
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    HIRE_STATUS_CHOICES = (
        ('pending', 'Pending'),     
        ('released', 'Released'),   
        ('cancelled', 'Cancelled'),
    )

    
    payer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buyer_payments')
    payee = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='artist_payments',
        blank=True, 
        null=True
    )
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    hire_status = models.CharField(max_length=20, choices=HIRE_STATUS_CHOICES, default='pending', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Payment 2FA fields
    requires_2fa_verification = models.BooleanField(default=False, help_text="Whether this payment requires 2FA verification")
    is_2fa_verified = models.BooleanField(default=False, help_text="Whether 2FA has been verified for this payment")
    verification_attempts = models.PositiveIntegerField(default=0, help_text="Number of failed verification attempts")
    verification_locked_until = models.DateTimeField(null=True, blank=True, help_text="When verification lock expires")
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def calculate_platform_fee(self, fee_percentage=5):
        """Calculate platform fee"""
        return (self.amount * Decimal(fee_percentage)) / Decimal(100)
    
    def calculate_artist_earning(self, fee_percentage=5):
        """Calculate artist earning after platform fee"""
        return self.amount - self.calculate_platform_fee(fee_percentage)
    
    def requires_2fa(self):
        """Check if payment requires 2FA verification"""
        # Define minimum amount for 2FA (can be configurable)
        MIN_2FA_AMOUNT = Decimal('5000.00')  # PKR 5000
        
        # Check if user has 2FA enabled and amount exceeds threshold
        return (self.payer.two_factor_enabled and 
                self.amount >= MIN_2FA_AMOUNT)
    
    def is_verification_locked(self):
        """Check if payment verification is locked due to failed attempts"""
        if self.verification_locked_until:
            return timezone.now() < self.verification_locked_until
        return False
    
    def __str__(self):
        return f"Payment #{self.transaction_id} - PKR{self.amount}"


class PaymentVerificationSession(models.Model):
    """Session for payment 2FA verification"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='verification_sessions')
    session_token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    verification_type = models.CharField(max_length=20, choices=[
        ('payment_confirm', 'Payment Confirmation'),
        ('payment_refund', 'Payment Refund'),
        ('payment_release', 'Payment Release')
    ], default='payment_confirm')
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Payment Verification for {self.payment.transaction_id}"







# Message Model
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(max_length=2000)
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

# Review Model
class Review(models.Model):
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['reviewer', 'job']
    
    def __str__(self):
        return f"Review for {self.artist.username} - {self.rating} stars"

# Contract Model
class Contract(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    )
    
    RIGHTS_CHOICES = (
        ('display_only', 'Display Only'),
        ('reproduction', 'Reproduction Rights'),
        ('commercial', 'Commercial Use'),
        ('exclusive', 'Exclusive Rights'),
    )
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='contract')
    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='artist_contracts')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buyer_contracts')
    terms = models.TextField(max_length=5000)
    rights_type = models.CharField(max_length=20, choices=RIGHTS_CHOICES, default='display_only')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    artist_signed = models.BooleanField(default=False)
    buyer_signed = models.BooleanField(default=False)
    artist_signed_at = models.DateTimeField(null=True, blank=True)
    buyer_signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_fully_signed(self):
        """Check if contract is signed by both parties"""
        return self.artist_signed and self.buyer_signed
    
    def sign_by_artist(self):
        """Sign contract by artist"""
        self.artist_signed = True
        self.artist_signed_at = timezone.now()
        if self.buyer_signed:
            self.status = 'active'
        self.save()
    
    def sign_by_buyer(self):
        """Sign contract by buyer"""
        self.buyer_signed = True
        self.buyer_signed_at = timezone.now()
        if self.artist_signed:
            self.status = 'active'
        self.save()
    
    def __str__(self):
        return f"Contract for {self.job.title}"

# Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_bid', 'New Bid'),
        ('bid_accepted', 'Bid Accepted'),
        ('job_completed', 'Job Completed'),
        ('payment_received', 'Payment Received'),
        ('new_message', 'New Message'),
        ('contract_signed', 'Contract Signed'),
    )
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

# Analytics Model for Admin Dashboard
class PlatformAnalytics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_users = models.PositiveIntegerField(default=0)
    total_artists = models.PositiveIntegerField(default=0)
    total_buyers = models.PositiveIntegerField(default=0)
    total_jobs_posted = models.PositiveIntegerField(default=0)
    total_jobs_completed = models.PositiveIntegerField(default=0)
    total_artworks_uploaded = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_platform_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    def calculate_daily_stats(self):
        """Calculate daily statistics"""
        # Users
        self.total_users = CustomUser.objects.count()
        self.total_artists = CustomUser.objects.filter(user_type='artist').count()
        self.total_buyers = CustomUser.objects.filter(user_type='buyer').count()
        
        # Jobs
        self.total_jobs_posted = Job.objects.count()
        self.total_jobs_completed = Job.objects.filter(status='completed').count()
        
        # Artworks
        self.total_artworks_uploaded = Artwork.objects.count()
        
        # Revenue
        completed_payments = Payment.objects.filter(status='completed')
        self.total_revenue = completed_payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Platform fees (assuming 5% fee)
        self.total_platform_fees = self.total_revenue * Decimal('0.05')
        
        self.save()
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"
    
    


