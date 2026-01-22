# CultureUp - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Core Features](#core-features)
4. [File Structure Analysis](#file-structure-analysis)
5. [Database Models](#database-models)
6. [API Endpoints](#api-endpoints)
7. [Security Features](#security-features)
8. [Admin Features](#admin-features)
9. [Technology Stack](#technology-stack)
10. [Installation & Setup](#installation--setup)

---

## Project Overview

**CultureUp** is a sophisticated Django REST API-based art marketplace and freelance platform that connects artists with buyers. It serves as a complete ecosystem for:

- **Artwork Trading**: Buy and sell digital/physical artwork
- **Freelance Services**: Post jobs and hire artists
- **Payment Processing**: Secure payment handling with multiple methods
- **Contract Management**: Digital contracts with dual signing
- **Communication**: Built-in messaging system
- **Analytics**: Comprehensive platform analytics

### Target Users
- **Artists**: Sell artwork, offer freelance services, build portfolios
- **Buyers**: Purchase artwork, post jobs, hire artists
- **Admins**: Manage platform, moderate content, handle payments

---

## System Architecture

### Backend Framework
- **Django 5.2**: Main web framework
- **Django REST Framework**: API development
- **SQLite/PostgreSQL**: Database management
- **Token Authentication**: Secure API access

### Key Components
1. **Authentication System**: Custom user model with role-based access
2. **Media Management**: Image processing and watermarking
3. **Payment Gateway**: Stripe integration with multiple payment methods
4. **Notification System**: Email and in-app notifications
5. **Admin Dashboard**: Comprehensive management interface

---

## Core Features

### 1. Authentication & User Management

#### Custom User System
- **Three User Types**: Artist, Buyer, Admin
- **Profile Management**: Separate profiles for artists and buyers
- **Email Verification**: Account verification system
- **Password Security**: Django's built-in password validation

#### Two-Factor Authentication (2FA)
- **TOTP Implementation**: Time-based One-Time Password
- **QR Code Generation**: Easy setup with authenticator apps
- **Backup Codes**: Account recovery mechanism
- **Session Management**: Temporary 2FA sessions

**Key Files:**
- `api/models.py` - CustomUser, TwoFactorSession models
- `api/two_factor_serializers.py` - 2FA API serializers
- `api/two_factor_utils.py` - 2FA utility functions

### 2. Artwork Management System

#### Core Artwork Features
- **Multiple Categories**: Organized artwork classification
- **Price Management**: Flexible pricing options
- **Featured System**: Highlight premium artwork
- **View Tracking**: Monitor artwork popularity
- **Like System**: User engagement tracking

#### Advanced Image Processing
- **Automatic Watermarking**: Diagonal text overlay protection
- **Duplicate Detection**: Perceptual hash-based duplicate prevention
- **Image Validation**: File type and size validation
- **Multiple Formats**: Support for various image formats

#### Duplicate Detection Algorithm
```python
# Uses imagehash library for perceptual hashing
- Average Hash (aHash): Basic similarity detection
- Difference Hash (dHash): Edge-based comparison
- Perceptual Hash (pHash): Advanced similarity detection
- Wavelet Hash (wHash): Frequency-based analysis
```

**Key Files:**
- `api/models.py` - Artwork, ArtworkLike models
- `api/image_validators.py` - Image validation logic
- `api/management/commands/generate_artwork_hashes.py` - Hash generation
- `api/management/commands/find_duplicates.py` - Duplicate detection

### 3. Job & Freelance System

#### Job Management
- **Job Posting**: Buyers create job listings
- **Bid System**: Artists submit competitive bids
- **Skill Matching**: Match jobs with artist skills
- **Budget Management**: Flexible budget ranges
- **Deadline Tracking**: Project timeline management

#### Hiring Process
1. **Job Creation**: Buyer posts job requirements
2. **Bid Submission**: Artists submit proposals
3. **Bid Selection**: Buyer chooses preferred artist
4. **Contract Creation**: Automatic contract generation
5. **Payment Escrow**: Secure payment holding
6. **Project Completion**: Milestone-based delivery
7. **Payment Release**: Automatic payment to artist

**Key Files:**
- `api/models.py` - Job, Bid models
- `api/views.py` - Job and bid management APIs
- `api/serializers.py` - Job/bid serializers

### 4. Payment Processing System

#### Multiple Payment Methods
- **Stripe Integration**: Credit/debit card processing
- **JazzCash**: Mobile wallet integration
- **Bank Transfer**: Direct bank payments
- **Cash on Delivery**: Physical payment option

#### Payment Features
- **Escrow System**: Secure payment holding
- **Platform Fees**: Automatic 5% commission calculation
- **Refund Processing**: Automated refund handling
- **3D Secure**: Enhanced security for card payments
- **Transaction Tracking**: Complete payment history

#### Payment Flow
1. **Order Creation**: User initiates purchase
2. **Payment Method Selection**: Choose payment option
3. **Payment Processing**: Secure transaction handling
4. **Confirmation**: Payment verification
5. **Escrow Holding**: Funds held securely
6. **Release Trigger**: Payment released on completion

**Key Files:**
- `api/models.py` - Payment, Order models
- `api/views.py` - Payment processing APIs
- `main/settings.py` - Stripe configuration

### 5. Messaging & Communication

#### Direct Messaging
- **User-to-User**: Private conversations
- **Job-Related**: Project-specific discussions
- **File Attachments**: Share documents and images
- **Read Status**: Message tracking
- **Conversation Threading**: Organized message history

#### Notification System
- **Multiple Types**: Bid notifications, payment alerts, messages
- **Email Integration**: Automated email notifications
- **In-App Notifications**: Real-time platform notifications
- **Read/Unread Tracking**: Notification status management

**Key Files:**
- `api/models.py` - Message, Notification models
- `api/notifications/utils.py` - Notification utilities
- `api/email_service.py` - Email handling

### 6. Contract Management

#### Digital Contracts
- **Automatic Generation**: Contract creation from job details
- **Rights Management**: Different usage rights (display, reproduction, commercial, exclusive)
- **Dual Signing**: Both parties must sign
- **Deadline Tracking**: Contract timeline management
- **Status Monitoring**: Contract lifecycle tracking

#### Contract Types
- **Display Only**: Limited viewing rights
- **Reproduction**: Printing and copying rights
- **Commercial**: Business usage rights
- **Exclusive**: Full ownership transfer

**Key Files:**
- `api/models.py` - Contract model
- `api/views.py` - Contract management APIs

### 7. Equipment Marketplace

#### Equipment Management
- **Multiple Categories**: Frame, paint, brush, canvas, other
- **Stock Tracking**: Inventory management
- **Price Management**: Flexible pricing
- **Availability Status**: Real-time stock updates
- **Order Integration**: Seamless purchasing

**Key Files:**
- `api/models.py` - Equipment, EquipmentOrderItem models
- `api/views.py` - Equipment management APIs

### 8. Review & Rating System

#### Artist Reviews
- **5-Star Rating**: Standard rating system
- **Written Reviews**: Detailed feedback
- **Job-Based**: Reviews tied to completed projects
- **Unique Constraint**: One review per job
- **Rating Aggregation**: Automatic average calculation

#### Rating Impact
- **Artist Profiles**: Ratings displayed on profiles
- **Search Ranking**: Higher-rated artists get better visibility
- **Trust Building**: Reputation system for platform trust

**Key Files:**
- `api/models.py` - Review model
- `api/views.py` - Review management APIs

---

## File Structure Analysis

### Main Application Structure

#### `/main/` - Django Project Configuration
- **`settings.py`**: Core Django settings, database config, installed apps
- **`urls.py`**: Main URL routing
- **`wsgi.py`**: WSGI application entry point
- **`asgi.py`**: ASGI application for async support

#### `/api/` - Core Application Logic
- **`models.py`**: Database models (20+ models)
- **`views.py`**: Main API endpoints (50+ endpoints)
- **`serializers.py`**: Data serialization for APIs
- **`urls.py`**: API URL routing
- **`permissions.py`**: Custom permission classes
- **`filters.py`**: Advanced filtering logic

#### Authentication & Security
- **`two_factor_serializers.py`**: 2FA API serializers
- **`two_factor_utils.py`**: 2FA utility functions
- **`image_validators.py`**: Image validation logic

#### Admin Features
- **`admin.py`**: Django admin configuration
- **`admin_views.py`**: Custom admin API endpoints
- **`admin_serializers.py`**: Admin-specific serializers
- **`admin_urls.py`**: Admin URL routing

#### Utilities & Services
- **`email_service.py`**: Email handling
- **`email_views.py`**: Email-related APIs
- **`signals.py`**: Django signals for automated actions
- **`notifications/utils.py`**: Notification utilities

#### Management Commands
- **`management/commands/generate_artwork_hashes.py`**: Generate perceptual hashes
- **`management/commands/find_duplicates.py`**: Find duplicate artworks

#### Database Migrations
- **`migrations/`**: 20+ migration files tracking database changes

### Media & Static Files

#### `/media/` - User Uploaded Content
- **`artworks/`**: Original artwork images
- **`watermarked_artworks/`**: Processed images with watermarks
- **`profile_images/`**: User profile pictures
- **`equipment/`**: Equipment images
- **`message_attachments/`**: File attachments in messages

#### `/staticfiles/` - Static Assets
- **`admin/`**: Django admin interface assets
- **`rest_framework/`**: DRF browsable API assets
- **`drf-yasg/`**: API documentation assets

#### `/templates/` - HTML Templates
- **`admin/`**: Custom admin templates
- **`emails/`**: Email templates (HTML and text)
- **`index.html`**: Main application template

---

## Database Models

### User Management Models

#### 1. CustomUser
```python
# Extended Django User with additional fields
- user_type: artist/buyer/admin
- phone_number: Contact information
- is_verified: Account verification status
- profile_image: User avatar
- two_factor_enabled: 2FA status
- two_factor_secret: TOTP secret key
- backup_codes: Recovery codes array
```

#### 2. ArtistProfile
```python
# Artist-specific information
- bio: Artist description
- skills: Comma-separated skills list
- experience_level: beginner/intermediate/expert
- hourly_rate: Freelance rate
- portfolio_description: Portfolio overview
- rating: Average rating from reviews
- total_projects_completed: Project count
- total_earnings: Lifetime earnings
- is_available: Availability status
```

#### 3. BuyerProfile
```python
# Buyer-specific information
- company_name: Business name
- company_address: Business address
- total_spent: Lifetime spending
- total_projects_posted: Posted job count
```

### Content Models

#### 4. Artwork
```python
# Artwork listings with advanced features
- title: Artwork name
- description: Detailed description
- category: Artwork category
- price: Selling price
- image: Original image file
- watermarked_image: Protected image
- is_featured: Featured status
- views_count: View tracking
- ahash, dhash, phash, whash: Perceptual hashes
```

#### 5. Job
```python
# Freelance job postings
- title: Job title
- description: Job requirements
- category: Job category
- budget_min/max: Budget range
- experience_required: Required skill level
- deadline: Project deadline
- status: open/in_progress/completed/cancelled
```

#### 6. Equipment
```python
# Equipment marketplace items
- name: Equipment name
- description: Equipment details
- equipment_type: frame/paint/brush/canvas/other
- price: Equipment price
- stock_quantity: Available stock
- is_available: Availability status
```

### Transaction Models

#### 7. Payment
```python
# Payment transaction records
- amount: Payment amount
- payment_method: stripe/jazzcash/bank_transfer/cod
- status: pending/completed/failed/refunded
- stripe_payment_intent: Stripe transaction ID
- hire_status: pending/released/cancelled
- platform_fee: Commission amount
```

#### 8. Order
```python
# Purchase orders
- total_amount: Order total
- status: pending/confirmed/shipped/delivered/cancelled
- shipping_address: Delivery address
- created_at: Order timestamp
```

### Communication Models

#### 9. Message
```python
# User messaging system
- sender: Message sender
- recipient: Message recipient
- content: Message text
- attachment: File attachment
- is_read: Read status
- job: Related job (optional)
```

#### 10. Notification
```python
# Platform notifications
- recipient: Notification recipient
- notification_type: Type of notification
- title: Notification title
- message: Notification content
- is_read: Read status
- related_object_id: Related content ID
```

### Business Logic Models

#### 11. Contract
```python
# Digital contracts
- job: Related job
- artist: Contract artist
- buyer: Contract buyer
- rights_type: display_only/reproduction/commercial/exclusive
- artist_signed: Artist signature status
- buyer_signed: Buyer signature status
- status: active/completed/terminated
```

#### 12. Review
```python
# Artist reviews
- job: Related completed job
- reviewer: Review author (buyer)
- artist: Reviewed artist
- rating: 1-5 star rating
- comment: Written feedback
```

#### 13. Bid
```python
# Job bids from artists
- job: Target job
- artist: Bidding artist
- amount: Bid amount
- proposal: Bid description
- status: pending/accepted/rejected
```

---

## API Endpoints

### Authentication Endpoints
```
POST /api/register/ - User registration
POST /api/login/ - User login with 2FA support
POST /api/logout/ - User logout
GET /api/profile/ - Get user profile
PUT /api/profile/ - Update user profile
```

### Two-Factor Authentication
```
POST /api/2fa/setup/ - Initialize 2FA setup
POST /api/2fa/enable/ - Enable 2FA
POST /api/2fa/disable/ - Disable 2FA
POST /api/2fa/verify/ - Verify 2FA code
GET /api/2fa/status/ - Check 2FA status
POST /api/2fa/backup-codes/ - Generate backup codes
```

### Artwork Management
```
GET /api/artworks/ - List artworks with filtering
POST /api/artworks/ - Create new artwork
GET /api/artworks/{id}/ - Get artwork details
PUT /api/artworks/{id}/ - Update artwork
DELETE /api/artworks/{id}/ - Delete artwork
POST /api/artworks/{id}/like/ - Like/unlike artwork
GET /api/artworks/featured/ - Get featured artworks
```

### Job & Freelance System
```
GET /api/jobs/ - List jobs with filtering
POST /api/jobs/ - Create new job
GET /api/jobs/{id}/ - Get job details
PUT /api/jobs/{id}/ - Update job
DELETE /api/jobs/{id}/ - Delete job
POST /api/jobs/{id}/hire/ - Hire artist for job
POST /api/jobs/{id}/complete/ - Mark job complete

GET /api/bids/ - List bids
POST /api/bids/ - Submit bid
GET /api/bids/{id}/ - Get bid details
PUT /api/bids/{id}/ - Update bid
DELETE /api/bids/{id}/ - Delete bid
```

### Payment Processing
```
GET /api/payments/ - List payments
POST /api/payments/ - Create payment
GET /api/payments/{id}/ - Get payment details
POST /api/payments/{id}/confirm/ - Confirm payment
POST /api/payments/{id}/process/ - Process payment
```

### Equipment Marketplace
```
GET /api/equipment/ - List equipment
POST /api/equipment/ - Add equipment
GET /api/equipment/{id}/ - Get equipment details
PUT /api/equipment/{id}/ - Update equipment
DELETE /api/equipment/{id}/ - Delete equipment
```

### Orders & E-commerce
```
GET /api/orders/ - List orders
POST /api/orders/ - Create order
GET /api/orders/{id}/ - Get order details
POST /api/orders/{id}/confirm/ - Confirm order
POST /api/orders/{id}/cancel/ - Cancel order
```

### Communication
```
GET /api/messages/ - List messages
POST /api/messages/ - Send message
GET /api/messages/{id}/ - Get message details
POST /api/messages/{id}/mark-read/ - Mark as read
GET /api/conversations/ - List conversations

GET /api/notifications/ - List notifications
POST /api/notifications/{id}/mark-read/ - Mark notification read
GET /api/notifications/unread-count/ - Get unread count
```

### Reviews & Contracts
```
GET /api/reviews/ - List reviews
POST /api/reviews/ - Create review
GET /api/reviews/{id}/ - Get review details

GET /api/contracts/ - List contracts
POST /api/contracts/ - Create contract
POST /api/contracts/{id}/sign/ - Sign contract
POST /api/contracts/{id}/terminate/ - Terminate contract
```

### Admin Endpoints
```
GET /api/admin/users/ - Manage all users
POST /api/admin/users/{id}/verify/ - Verify user
POST /api/admin/users/{id}/activate/ - Activate user
GET /api/admin/artworks/ - Moderate artworks
POST /api/admin/artworks/{id}/approve/ - Approve artwork
GET /api/admin/payments/ - Manage payments
POST /api/admin/payments/{id}/refund/ - Process refund
GET /api/admin/analytics/ - Platform analytics
GET /api/admin/revenue-report/ - Revenue reports
```

---

## Security Features

### Authentication Security
- **Token-Based Authentication**: Secure API access
- **Password Validation**: Django's built-in validation
- **Two-Factor Authentication**: TOTP with backup codes
- **Session Management**: Secure session handling

### Data Protection
- **Input Validation**: Comprehensive data validation
- **SQL Injection Prevention**: Django ORM protection
- **XSS Protection**: Template auto-escaping
- **CSRF Protection**: Cross-site request forgery prevention

### File Security
- **Image Validation**: File type and size validation
- **Watermarking**: Automatic image protection
- **Secure Upload**: Protected file upload handling
- **Media Access Control**: Controlled file access

### Permission System
- **Role-Based Access**: Artist/Buyer/Admin permissions
- **Object-Level Permissions**: Fine-grained access control
- **Owner Verification**: Resource ownership validation
- **Admin Privileges**: Elevated access for administrators

---

## Admin Features

### User Management Dashboard
- **User Overview**: Complete user statistics
- **Account Verification**: Verify/unverify users
- **Account Status**: Activate/deactivate accounts
- **Staff Privileges**: Grant/revoke staff access
- **Bulk Operations**: Mass user management

### Content Moderation
- **Artwork Approval**: Approve/reject artwork submissions
- **Featured Content**: Manage featured artworks
- **Content Removal**: Remove inappropriate content
- **Category Management**: Organize content categories

### Financial Management
- **Payment Oversight**: Monitor all transactions
- **Refund Processing**: Handle payment refunds
- **Revenue Reports**: Detailed financial analytics
- **Artist Payments**: Release payments to artists
- **Platform Fees**: Commission tracking

### Analytics & Reporting
- **Real-Time Statistics**: Live platform metrics
- **User Growth**: Registration and activity trends
- **Revenue Analytics**: Income and expense tracking
- **Popular Content**: Most viewed/liked artworks
- **Performance Metrics**: Platform performance indicators

### System Administration
- **Job Management**: Close/reopen job postings
- **Equipment Management**: Manage equipment catalog
- **Email System**: Monitor email notifications
- **Database Management**: Data integrity checks

---

## Technology Stack

### Backend Technologies
- **Django 5.2**: Web framework
- **Django REST Framework**: API development
- **SQLite/PostgreSQL**: Database systems
- **Python 3.8+**: Programming language

### Authentication & Security
- **Django Token Authentication**: API security
- **pyotp**: Two-factor authentication
- **qrcode**: QR code generation
- **Django CORS Headers**: Cross-origin requests

### Payment Processing
- **Stripe**: Credit card processing
- **Multiple Gateways**: JazzCash, bank transfer, COD

### Image Processing
- **Pillow (PIL)**: Image manipulation
- **imagehash**: Perceptual hashing for duplicate detection
- **Custom Watermarking**: Diagonal text overlay

### API Documentation
- **drf-yasg**: Swagger/OpenAPI documentation
- **Django Filter**: Advanced filtering
- **Pagination**: Efficient data loading

### Email & Notifications
- **Django Email**: SMTP email handling
- **HTML Templates**: Rich email formatting
- **Real-time Notifications**: In-app notification system

---

## Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
Virtual environment (recommended)
```

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd cultureup-project
```

2. **Create Virtual Environment**
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
# Create .env file with:
SECRET_KEY=your-secret-key
DEBUG=True
STRIPE_PUBLISHABLE_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Static Files**
```bash
python manage.py collectstatic
```

7. **Run Development Server**
```bash
python manage.py runserver
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Admin Panel**: `http://localhost:8000/admin/`

### Testing
```bash
python manage.py test
```

---

## Conclusion

CultureUp is a comprehensive, production-ready art marketplace and freelance platform with enterprise-level features including:

- **Advanced Security**: 2FA, token authentication, permission system
- **Sophisticated Image Processing**: Watermarking and duplicate detection
- **Complete E-commerce**: Orders, payments, contracts, reviews
- **Professional Admin Tools**: User management, content moderation, analytics
- **Scalable Architecture**: RESTful APIs, efficient database design
- **Modern Technology Stack**: Latest Django, comprehensive integrations

The platform successfully bridges the gap between artists and buyers while providing robust tools for platform management and growth.

---

*This documentation covers all major features and functionality of the CultureUp platform. For specific implementation details, refer to the individual source files mentioned throughout this document.*