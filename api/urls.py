# urls.py - Complete App URLs Configuration
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create router and register viewsets
router = DefaultRouter()


# Register all viewsets
router.register(r'artist-profiles', ArtistProfileViewSet, basename='artist-profile')
router.register(r'buyer-profiles', BuyerProfileViewSet, basename='buyer-profile')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'artworks', ArtworkViewSet, basename='artwork')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'bids', BidViewSet, basename='bid')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'analytics', PlatformAnalyticsViewSet, basename='analytics')



# URL patterns
urlpatterns = [
    # ===== Authentication URLs =====
    path('auth/register/', register, name='api-register'),
    path('auth/login/', login, name='api-login'),
    path('auth/logout/', logout, name='api-logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    
    # ===== Dashboard & Stats =====
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    
    # ===== Global Search =====
    path('search/', global_search, name='global-search'),
    
    # ===== Artist Profile Custom Actions =====
    path('artist-profiles/<int:pk>/reviews/', 
         ArtistProfileViewSet.as_view({'get': 'reviews'}), 
         name='artist-reviews'),
    path('artist-profiles/<int:user_id>/artworks/', ArtworkViewSet.as_view({'get': 'list'}), name='artist-artworks'),

    


    
    # ===== Artwork Custom Actions =====
    path('artworks/<int:pk>/like/', 
         ArtworkViewSet.as_view({'post': 'like'}), 
         name='artwork-like'),
    path('artworks/featured/', 
         ArtworkViewSet.as_view({'get': 'featured'}), 
         name='featured-artworks'),
    
    # ===== Job Custom Actions =====
    path('jobs/<int:pk>/bids/', 
         JobViewSet.as_view({'get': 'bids'}), 
         name='job-bids'),
    path('jobs/<int:pk>/hire/', 
         JobViewSet.as_view({'post': 'hire_artist'}), 
         name='hire-artist'),
    path('jobs/<int:pk>/complete/', 
         JobViewSet.as_view({'post': 'complete_job'}), 
         name='complete-job'),
    
     path('jobs/<int:job_id>/payment-status/', job_payment_status, name='job-payment-status'),
     
    # ===== Equipment Custom Actions =====
    path('equipment/in-stock/', 
         EquipmentViewSet.as_view({'get': 'in_stock'}), 
         name='equipment-in-stock'),
    
    # ===== Order Custom Actions =====
    path('orders/<int:pk>/confirm/', 
         OrderViewSet.as_view({'post': 'confirm'}), 
         name='confirm-order'),
    path('orders/<int:pk>/cancel/', 
         OrderViewSet.as_view({'post': 'cancel'}), 
         name='cancel-order'),
    
    # ===== Payment Custom Actions =====
    path('payments/<int:pk>/process/', 
         PaymentViewSet.as_view({'post': 'process'}), 
         name='process-payment'),
    
    # ===== Message Custom Actions =====
    path('messages/<int:pk>/mark-read/', 
         MessageViewSet.as_view({'post': 'mark_read'}), 
         name='mark-message-read'),
    path('messages/conversations/', 
         MessageViewSet.as_view({'get': 'conversations'}), 
         name='message-conversations'),
    
    # ===== Contract Custom Actions =====
    path('contracts/<int:pk>/sign/', 
         ContractViewSet.as_view({'post': 'sign'}), 
         name='sign-contract'),
    
    # ===== Notification Custom Actions =====
    path('notifications/<int:pk>/mark-read/', 
         NotificationViewSet.as_view({'post': 'mark_read'}), 
         name='mark-notification-read'),
    path('notifications/mark-all-read/', 
         NotificationViewSet.as_view({'post': 'mark_all_read'}), 
         name='mark-all-notifications-read'),
    path('notifications/unread-count/', 
         NotificationViewSet.as_view({'get': 'unread_count'}), 
         name='unread-notifications-count'),
    
    # ===== Analytics Custom Actions =====
    path('analytics/calculate-today/', 
         PlatformAnalyticsViewSet.as_view({'post': 'calculate_today'}), 
         name='calculate-today-analytics'),
    
    path('', include(router.urls)),
]



"""
Available Endpoints Summary:

AUTHENTICATION:
- POST   /api/auth/register/
- POST   /api/auth/login/
- POST   /api/auth/logout/
- GET    /api/auth/profile/
- PATCH  /api/auth/profile/

ARTIST PROFILES:
- GET    /api/artist-profiles/
- POST   /api/artist-profiles/
- GET    /api/artist-profiles/{id}/
- PUT    /api/artist-profiles/{id}/
- PATCH  /api/artist-profiles/{id}/
- DELETE /api/artist-profiles/{id}/
- GET    /api/artist-profiles/{id}/reviews/
- GET    /api/artist-profiles/{id}/artworks/

BUYER PROFILES:
- GET    /api/buyer-profiles/
- POST   /api/buyer-profiles/
- GET    /api/buyer-profiles/{id}/
- PUT    /api/buyer-profiles/{id}/
- PATCH  /api/buyer-profiles/{id}/
- DELETE /api/buyer-profiles/{id}/

CATEGORIES:
- GET    /api/categories/
- GET    /api/categories/{id}/

ARTWORKS:
- GET    /api/artworks/
- POST   /api/artworks/
- GET    /api/artworks/{id}/
- PUT    /api/artworks/{id}/
- PATCH  /api/artworks/{id}/
- DELETE /api/artworks/{id}/
- POST   /api/artworks/{id}/like/
- GET    /api/artworks/featured/

JOBS:
- GET    /api/jobs/
- POST   /api/jobs/
- GET    /api/jobs/{id}/
- PUT    /api/jobs/{id}/
- PATCH  /api/jobs/{id}/
- DELETE /api/jobs/{id}/
- GET    /api/jobs/{id}/bids/
- POST   /api/jobs/{id}/hire/
- POST   /api/jobs/{id}/complete/

BIDS:
- GET    /api/bids/
- POST   /api/bids/
- GET    /api/bids/{id}/
- PUT    /api/bids/{id}/
- PATCH  /api/bids/{id}/
- DELETE /api/bids/{id}/

EQUIPMENT:
- GET    /api/equipment/
- POST   /api/equipment/
- GET    /api/equipment/{id}/
- PUT    /api/equipment/{id}/
- PATCH  /api/equipment/{id}/
- DELETE /api/equipment/{id}/
- GET    /api/equipment/in-stock/

ORDERS:
- GET    /api/orders/
- POST   /api/orders/
- GET    /api/orders/{id}/
- PUT    /api/orders/{id}/
- PATCH  /api/orders/{id}/
- DELETE /api/orders/{id}/
- POST   /api/orders/{id}/confirm/
- POST   /api/orders/{id}/cancel/

PAYMENTS:
- GET    /api/payments/
- POST   /api/payments/
- GET    /api/payments/{id}/
- POST   /api/payments/{id}/process/

MESSAGES:
- GET    /api/messages/
- POST   /api/messages/
- GET    /api/messages/{id}/
- PUT    /api/messages/{id}/
- PATCH  /api/messages/{id}/
- DELETE /api/messages/{id}/
- POST   /api/messages/{id}/mark-read/
- GET    /api/messages/conversations/

REVIEWS:
- GET    /api/reviews/
- POST   /api/reviews/
- GET    /api/reviews/{id}/
- PUT    /api/reviews/{id}/
- PATCH  /api/reviews/{id}/
- DELETE /api/reviews/{id}/

CONTRACTS:
- GET    /api/contracts/
- POST   /api/contracts/
- GET    /api/contracts/{id}/
- PUT    /api/contracts/{id}/
- PATCH  /api/contracts/{id}/
- DELETE /api/contracts/{id}/
- POST   /api/contracts/{id}/sign/

NOTIFICATIONS:
- GET    /api/notifications/
- GET    /api/notifications/{id}/
- POST   /api/notifications/{id}/mark-read/
- POST   /api/notifications/mark-all-read/
- GET    /api/notifications/unread-count/

ANALYTICS (Admin only):
- GET    /api/analytics/
- GET    /api/analytics/{id}/
- POST   /api/analytics/calculate-today/

SEARCH:
- GET    /api/search/?q=keyword

DASHBOARD:
- GET    /api/dashboard/stats/
"""


