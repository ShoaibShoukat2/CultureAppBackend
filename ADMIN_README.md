# 🎨 ArtConnect Admin Backend - Comprehensive Management System

## Overview
A complete admin backend system for the ArtConnect platform with powerful APIs, dashboard, and management tools.

## 🚀 Features

### 👥 User Management
- **Complete CRUD operations** for all user types (Artists, Buyers, Admins)
- **User verification** and account activation controls
- **Staff privileges** management
- **Bulk operations** for efficient user management
- **Advanced filtering** and search capabilities
- **User statistics** and analytics

### 🎨 Artwork Management
- **Content moderation** with approval/rejection system
- **Featured artwork** management
- **AI-powered duplicate detection** using AWS Rekognition
- **Bulk artwork operations**
- **Moderation status tracking**
- **Advanced artwork analytics**

### 💼 Job & Project Management
- **Complete job lifecycle** management
- **Admin override capabilities** (close/reopen jobs)
- **Bid monitoring** and statistics
- **Project completion tracking**
- **Advanced job analytics**

### 💳 Payment Management
- **Payment oversight** and monitoring
- **Refund processing** capabilities
- **Payment release controls** for hire payments
- **Revenue tracking** and analytics
- **Stripe integration** monitoring
- **Financial reporting**

### 📊 Analytics & Reporting
- **Real-time dashboard** with comprehensive statistics
- **Revenue reports** with date filtering
- **User growth analytics**
- **Platform performance metrics**
- **Custom date range reports**

### 🛠️ System Management
- **Category management** with activation controls
- **Equipment inventory** management
- **Order management** with admin overrides
- **Notification system** oversight
- **Bulk operations** for efficiency

## 🔧 Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Setup Admin Users
```bash
# Create superuser and sample data
python manage.py setup_admin --create-superuser --create-sample-data

# Or create just superuser
python manage.py setup_admin --create-superuser --admin-username admin --admin-email admin@artconnect.com --admin-password admin123
```

### 3. Access Admin Panel
- **Django Admin**: `http://localhost:8000/admin/`
- **API Dashboard**: `http://localhost:8000/api/admin/dashboard/`
- **Revenue Report**: `http://localhost:8000/api/admin/revenue-report/`

## 📡 API Endpoints

### Authentication Required
All admin endpoints require authentication with admin/staff privileges.

### Dashboard & Analytics
```
GET  /api/admin/dashboard/                    - Comprehensive dashboard stats
GET  /api/admin/revenue-report/              - Revenue report with date filters
```

### User Management
```
GET    /api/admin/users/                      - List all users
POST   /api/admin/users/                      - Create user
GET    /api/admin/users/{id}/                 - Get user details
PUT    /api/admin/users/{id}/                 - Update user
DELETE /api/admin/users/{id}/                 - Delete user
POST   /api/admin/users/{id}/verify/          - Verify user
POST   /api/admin/users/{id}/unverify/        - Unverify user
POST   /api/admin/users/{id}/activate/        - Activate user
POST   /api/admin/users/{id}/deactivate/      - Deactivate user
POST   /api/admin/users/{id}/make-staff/      - Make user staff
POST   /api/admin/users/{id}/remove-staff/    - Remove staff privileges
GET    /api/admin/users/stats/                - User statistics
POST   /api/admin/bulk/users/                 - Bulk user actions
```

### Artwork Management
```
GET    /api/admin/artworks/                   - List all artworks
GET    /api/admin/artworks/{id}/              - Get artwork details
PUT    /api/admin/artworks/{id}/              - Update artwork
DELETE /api/admin/artworks/{id}/              - Delete artwork
POST   /api/admin/artworks/{id}/feature/      - Feature artwork
POST   /api/admin/artworks/{id}/unfeature/    - Unfeature artwork
POST   /api/admin/artworks/{id}/approve/      - Approve artwork
POST   /api/admin/artworks/{id}/reject/       - Reject artwork
GET    /api/admin/artworks/stats/             - Artwork statistics
POST   /api/admin/bulk/artworks/              - Bulk artwork actions
```

### Job Management
```
GET    /api/admin/jobs/                       - List all jobs
GET    /api/admin/jobs/{id}/                  - Get job details
PUT    /api/admin/jobs/{id}/                  - Update job
DELETE /api/admin/jobs/{id}/                  - Delete job
POST   /api/admin/jobs/{id}/close/            - Close job
POST   /api/admin/jobs/{id}/reopen/           - Reopen job
GET    /api/admin/jobs/stats/                 - Job statistics
```

### Payment Management
```
GET    /api/admin/payments/                   - List all payments
GET    /api/admin/payments/{id}/              - Get payment details
POST   /api/admin/payments/{id}/refund/       - Refund payment
POST   /api/admin/payments/{id}/release/      - Release hire payment
GET    /api/admin/payments/stats/             - Payment statistics
```

## 🔐 Permissions & Security

### Admin Permission Classes
- `IsAdminOrStaff`: Restricts access to admin users and staff only
- All endpoints require proper authentication
- CSRF protection enabled for state-changing operations

### User Types with Admin Access
- **Superuser**: Full system access
- **Admin**: Complete platform management
- **Staff**: Limited administrative functions

## 📊 Dashboard Features

### Real-time Statistics
- Total users, artists, buyers
- Revenue tracking and growth
- Active jobs and completed projects
- Artwork statistics and moderation queue
- Recent activity monitoring

### Quick Actions
- User verification and activation
- Artwork approval and featuring
- Payment processing and refunds
- Job management and closure

### Advanced Analytics
- User growth trends
- Revenue analysis by date range
- Platform performance metrics
- Top artists and buyers
- Payment method analysis

## 🛠️ Bulk Operations

### User Bulk Actions
```json
POST /api/admin/bulk/users/
{
  "user_ids": [1, 2, 3],
  "action": "verify"  // verify, unverify, activate, deactivate, make_staff, remove_staff
}
```

### Artwork Bulk Actions
```json
POST /api/admin/bulk/artworks/
{
  "artwork_ids": [1, 2, 3],
  "action": "approve"  // feature, unfeature, approve, reject
}
```

## 📈 Revenue Reporting

### Date Range Reports
```
GET /api/admin/revenue-report/?start_date=2024-01-01&end_date=2024-12-31
```

### Report Features
- Revenue by payment method
- Daily revenue breakdown
- Top earning artists
- Top spending buyers
- Transaction analysis

## 🎯 Admin Dashboard UI

### Enhanced Django Admin
- Custom dashboard with real-time stats
- Quick action buttons for common tasks
- Advanced filtering and search
- Bulk operations support
- Professional styling and UX

### Features
- **User Management**: Verify, activate, manage staff privileges
- **Content Moderation**: Approve/reject artworks, feature content
- **Payment Oversight**: Process refunds, release payments
- **Analytics**: Comprehensive platform statistics
- **Quick Actions**: One-click common operations

## 🔧 Customization

### Adding New Admin Features
1. Create views in `admin_views.py`
2. Add serializers in `admin_serializers.py`
3. Update URLs in `admin_urls.py`
4. Add permissions as needed

### Custom Dashboard Widgets
- Extend the dashboard template
- Add new API endpoints for data
- Update JavaScript for real-time updates

## 🚀 Production Deployment

### Environment Variables
```env
# Admin settings
ADMIN_EMAIL=admin@yourplatform.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here
```

### Security Considerations
- Use strong passwords for admin accounts
- Enable HTTPS in production
- Configure proper CORS settings
- Set up rate limiting for admin endpoints
- Regular security audits

## 📝 Usage Examples

### Create Admin User
```python
from django.contrib.auth import get_user_model
User = get_user_model()

admin = User.objects.create_superuser(
    username='admin',
    email='admin@artconnect.com',
    password='secure_password',
    user_type='admin'
)
```

### Bulk User Verification
```python
# Via API
import requests

response = requests.post('/api/admin/bulk/users/', {
    'user_ids': [1, 2, 3, 4, 5],
    'action': 'verify'
}, headers={'Authorization': 'Token your_admin_token'})
```

### Revenue Analysis
```python
# Get revenue report
response = requests.get('/api/admin/revenue-report/', {
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
}, headers={'Authorization': 'Token your_admin_token'})
```

## 🎉 Success! 

Your ArtConnect platform now has a comprehensive admin backend with:
- ✅ Complete user management system
- ✅ Advanced content moderation
- ✅ Financial oversight and reporting
- ✅ Real-time analytics dashboard
- ✅ Bulk operations for efficiency
- ✅ Professional admin interface
- ✅ Secure API endpoints
- ✅ Comprehensive documentation

The admin system provides everything needed to manage and monitor your art marketplace platform effectively!