# admin_urls.py - Admin-specific URL configuration
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import *

# Create admin router
admin_router = DefaultRouter()

# Register admin viewsets
admin_router.register(r'users', AdminUserManagementViewSet, basename='admin-users')
admin_router.register(r'artworks', AdminArtworkManagementViewSet, basename='admin-artworks')
admin_router.register(r'jobs', AdminJobManagementViewSet, basename='admin-jobs')
admin_router.register(r'payments', AdminPaymentManagementViewSet, basename='admin-payments')
admin_router.register(r'categories', AdminCategoryManagementViewSet, basename='admin-categories')
admin_router.register(r'equipment', AdminEquipmentManagementViewSet, basename='admin-equipment')
admin_router.register(r'orders', AdminOrderManagementViewSet, basename='admin-orders')

# Admin URL patterns
admin_urlpatterns = [
    # ===== Dashboard & Analytics =====
    path('dashboard/', admin_dashboard_stats, name='admin-dashboard'),
    path('revenue-report/', admin_revenue_report, name='admin-revenue-report'),
    
    # ===== User Management Actions =====
    path('users/<int:pk>/verify/', 
         AdminUserManagementViewSet.as_view({'post': 'verify_user'}), 
         name='admin-verify-user'),
    path('users/<int:pk>/unverify/', 
         AdminUserManagementViewSet.as_view({'post': 'unverify_user'}), 
         name='admin-unverify-user'),
    path('users/<int:pk>/activate/', 
         AdminUserManagementViewSet.as_view({'post': 'activate_user'}), 
         name='admin-activate-user'),
    path('users/<int:pk>/deactivate/', 
         AdminUserManagementViewSet.as_view({'post': 'deactivate_user'}), 
         name='admin-deactivate-user'),
    path('users/<int:pk>/make-staff/', 
         AdminUserManagementViewSet.as_view({'post': 'make_staff'}), 
         name='admin-make-staff'),
    path('users/<int:pk>/remove-staff/', 
         AdminUserManagementViewSet.as_view({'post': 'remove_staff'}), 
         name='admin-remove-staff'),
    path('users/stats/', 
         AdminUserManagementViewSet.as_view({'get': 'user_stats'}), 
         name='admin-user-stats'),
    
    # ===== Artwork Management Actions =====
    path('artworks/<int:pk>/feature/', 
         AdminArtworkManagementViewSet.as_view({'post': 'feature_artwork'}), 
         name='admin-feature-artwork'),
    path('artworks/<int:pk>/unfeature/', 
         AdminArtworkManagementViewSet.as_view({'post': 'unfeature_artwork'}), 
         name='admin-unfeature-artwork'),
    path('artworks/<int:pk>/approve/', 
         AdminArtworkManagementViewSet.as_view({'post': 'approve_artwork'}), 
         name='admin-approve-artwork'),
    path('artworks/<int:pk>/reject/', 
         AdminArtworkManagementViewSet.as_view({'post': 'reject_artwork'}), 
         name='admin-reject-artwork'),
    path('artworks/stats/', 
         AdminArtworkManagementViewSet.as_view({'get': 'artwork_stats'}), 
         name='admin-artwork-stats'),
    
    # ===== Job Management Actions =====
    path('jobs/<int:pk>/close/', 
         AdminJobManagementViewSet.as_view({'post': 'close_job'}), 
         name='admin-close-job'),
    path('jobs/<int:pk>/reopen/', 
         AdminJobManagementViewSet.as_view({'post': 'reopen_job'}), 
         name='admin-reopen-job'),
    path('jobs/stats/', 
         AdminJobManagementViewSet.as_view({'get': 'job_stats'}), 
         name='admin-job-stats'),
    
    # ===== Payment Management Actions =====
    path('payments/<int:pk>/refund/', 
         AdminPaymentManagementViewSet.as_view({'post': 'refund_payment'}), 
         name='admin-refund-payment'),
    path('payments/<int:pk>/release/', 
         AdminPaymentManagementViewSet.as_view({'post': 'release_payment'}), 
         name='admin-release-payment'),
    path('payments/stats/', 
         AdminPaymentManagementViewSet.as_view({'get': 'payment_stats'}), 
         name='admin-payment-stats'),
    
    # ===== Category Management Actions =====
    path('categories/<int:pk>/activate/', 
         AdminCategoryManagementViewSet.as_view({'post': 'activate_category'}), 
         name='admin-activate-category'),
    path('categories/<int:pk>/deactivate/', 
         AdminCategoryManagementViewSet.as_view({'post': 'deactivate_category'}), 
         name='admin-deactivate-category'),
    
    # ===== Equipment Management Actions =====
    path('equipment/<int:pk>/update-stock/', 
         AdminEquipmentManagementViewSet.as_view({'post': 'update_stock'}), 
         name='admin-update-equipment-stock'),
    
    # ===== Order Management Actions =====
    path('orders/<int:pk>/force-complete/', 
         AdminOrderManagementViewSet.as_view({'post': 'force_complete'}), 
         name='admin-force-complete-order'),
    path('orders/<int:pk>/cancel/', 
         AdminOrderManagementViewSet.as_view({'post': 'cancel_order'}), 
         name='admin-cancel-order'),
    
    # ===== Bulk Actions =====
    path('bulk/users/', bulk_user_action, name='admin-bulk-user-action'),
    path('bulk/artworks/', bulk_artwork_action, name='admin-bulk-artwork-action'),
    
    # Include router URLs
    path('', include(admin_router.urls)),
]

"""
Admin API Endpoints Summary:

DASHBOARD & ANALYTICS:
- GET    /api/admin/dashboard/                    - Comprehensive admin dashboard stats
- GET    /api/admin/revenue-report/              - Detailed revenue report with date filters

USER MANAGEMENT:
- GET    /api/admin/users/                       - List all users with admin details
- POST   /api/admin/users/                       - Create new user (admin)
- GET    /api/admin/users/{id}/                  - Get user details
- PUT    /api/admin/users/{id}/                  - Update user
- DELETE /api/admin/users/{id}/                  - Delete user
- POST   /api/admin/users/{id}/verify/           - Verify user account
- POST   /api/admin/users/{id}/unverify/         - Unverify user account
- POST   /api/admin/users/{id}/activate/         - Activate user account
- POST   /api/admin/users/{id}/deactivate/       - Deactivate user account
- POST   /api/admin/users/{id}/make-staff/       - Make user staff
- POST   /api/admin/users/{id}/remove-staff/     - Remove staff privileges
- GET    /api/admin/users/stats/                 - User statistics
- POST   /api/admin/bulk/users/                  - Bulk user actions

ARTWORK MANAGEMENT:
- GET    /api/admin/artworks/                    - List all artworks with moderation info
- GET    /api/admin/artworks/{id}/               - Get artwork details
- PUT    /api/admin/artworks/{id}/               - Update artwork
- DELETE /api/admin/artworks/{id}/               - Delete artwork
- POST   /api/admin/artworks/{id}/feature/       - Feature artwork
- POST   /api/admin/artworks/{id}/unfeature/     - Unfeature artwork
- POST   /api/admin/artworks/{id}/approve/       - Approve artwork
- POST   /api/admin/artworks/{id}/reject/        - Reject artwork
- GET    /api/admin/artworks/stats/              - Artwork statistics
- POST   /api/admin/bulk/artworks/               - Bulk artwork actions

JOB MANAGEMENT:
- GET    /api/admin/jobs/                        - List all jobs
- GET    /api/admin/jobs/{id}/                   - Get job details
- PUT    /api/admin/jobs/{id}/                   - Update job
- DELETE /api/admin/jobs/{id}/                   - Delete job
- POST   /api/admin/jobs/{id}/close/             - Close job (admin action)
- POST   /api/admin/jobs/{id}/reopen/            - Reopen job
- GET    /api/admin/jobs/stats/                  - Job statistics

PAYMENT MANAGEMENT:
- GET    /api/admin/payments/                    - List all payments
- GET    /api/admin/payments/{id}/               - Get payment details
- POST   /api/admin/payments/{id}/refund/        - Refund payment
- POST   /api/admin/payments/{id}/release/       - Release hire payment
- GET    /api/admin/payments/stats/              - Payment statistics

CATEGORY MANAGEMENT:
- GET    /api/admin/categories/                  - List all categories
- POST   /api/admin/categories/                  - Create category
- GET    /api/admin/categories/{id}/             - Get category details
- PUT    /api/admin/categories/{id}/             - Update category
- DELETE /api/admin/categories/{id}/             - Delete category
- POST   /api/admin/categories/{id}/activate/    - Activate category
- POST   /api/admin/categories/{id}/deactivate/  - Deactivate category

EQUIPMENT MANAGEMENT:
- GET    /api/admin/equipment/                   - List all equipment
- POST   /api/admin/equipment/                   - Create equipment
- GET    /api/admin/equipment/{id}/              - Get equipment details
- PUT    /api/admin/equipment/{id}/              - Update equipment
- DELETE /api/admin/equipment/{id}/              - Delete equipment
- POST   /api/admin/equipment/{id}/update-stock/ - Update stock quantity

ORDER MANAGEMENT:
- GET    /api/admin/orders/                      - List all orders
- GET    /api/admin/orders/{id}/                 - Get order details
- POST   /api/admin/orders/{id}/force-complete/  - Force complete order
- POST   /api/admin/orders/{id}/cancel/          - Cancel order (admin)

FEATURES:
✅ Comprehensive user management with verification, activation, staff controls
✅ Artwork moderation with approval/rejection, featuring, bulk actions
✅ Job management with admin override capabilities
✅ Payment oversight with refund and release controls
✅ Category and equipment management
✅ Order management with admin overrides
✅ Detailed analytics and reporting
✅ Bulk operations for efficiency
✅ Revenue reports with date filtering
✅ Real-time dashboard statistics
✅ Advanced filtering and search on all endpoints
✅ Proper admin permissions and security
"""