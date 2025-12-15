# 🎯 CultureUp - Complete API Documentation with Admin Backend

**Developed by:** Shoaib Shoukat - Full Stack Engineer

## 🆕 NEW: Comprehensive Admin Backend System

### 🔧 Admin Features
- ✅ **Complete User Management**: Verify, activate, manage all user accounts
- ✅ **Content Moderation**: Approve/reject artworks, feature content
- ✅ **Payment Oversight**: Process refunds, release payments, monitor transactions
- ✅ **Job Management**: Admin controls for jobs and projects
- ✅ **Analytics Dashboard**: Real-time platform statistics and reports
- ✅ **Bulk Operations**: Efficient mass actions for users and content
- ✅ **Revenue Reports**: Detailed financial analytics with date filtering
- ✅ **Professional Admin UI**: Enhanced Django admin with quick actions

### 🚀 Admin Quick Setup
1. **Create Admin Users**: `python manage.py setup_admin --create-superuser --create-sample-data`
2. **Access Admin Panel**: `http://localhost:8000/admin/`
3. **API Dashboard**: `http://localhost:8000/api/admin/dashboard/`
4. **Default Credentials**: 
   - Username: `admin`
   - Password: `admin123`
   - Email: `admin@artconnect.com`

## 🆕 NEW: AWS S3 Storage & Rekognition Duplicate Detection (Integrated)

### Features
- ✅ **AWS S3 Storage**: All artworks automatically stored in cloud
- ✅ **AI Duplicate Detection**: Automatic duplicate checking using AWS Rekognition
- ✅ **Security**: Prevents plagiarism and copyright infringement
- ✅ **Seamless Integration**: Works with existing `/api/artworks/` endpoints

### Quick Setup
1. Install: `pip install boto3`
2. Configure `.env` with AWS credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_STORAGE_BUCKET_NAME=your_bucket
   AWS_S3_REGION_NAME=us-east-1
   ```
3. Run: `python manage.py migrate`
4. Test: `python test_aws_connection.py`

### How It Works
- **Same endpoints** as before: `POST /api/artworks/`, `PUT /api/artworks/{id}/`, etc.
- **Automatic S3 upload** when creating/updating artworks
- **Automatic duplicate check** using AWS Rekognition AI
- **Automatic watermark** generation and S3 storage
- **No code changes needed** in your frontend!

---

## Base URL
```
http://localhost:8000/api/
```

---

## 📋 Table of Contents
1. [Admin Backend System](#admin-backend-system) **🆕 NEW**
2. [Authentication](#authentication)
3. [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa) **🆕 NEW**
4. [Artist Profiles](#artist-profiles)
5. [Buyer Profiles](#buyer-profiles)
6. [Artworks (with S3 & Rekognition)](#artworks)
7. [Jobs/Projects](#jobs-projects)
8. [Bids](#bids)
9. [Orders](#orders)
10. [Payments](#payments)
11. [Messages](#messages)
12. [Reviews](#reviews)
13. [Contracts](#contracts)
14. [Notifications](#notifications)
15. [Admin API Endpoints](#admin-api-endpoints) **🆕 NEW**

---

## 🛡️ Admin Backend System

### Overview
The ArtConnect platform includes a comprehensive admin backend system that provides complete control and oversight of the platform. This system includes both a web-based admin interface and powerful REST APIs for programmatic access.

### 🎯 Admin Capabilities

#### 👥 User Management
- **Complete User Control**: View, edit, verify, activate/deactivate all user accounts
- **User Type Management**: Manage artists, buyers, and admin accounts
- **Staff Privileges**: Grant and revoke staff access
- **Bulk Operations**: Perform actions on multiple users simultaneously
- **User Analytics**: Track user growth, activity, and engagement

#### 🎨 Content Moderation
- **Artwork Approval**: Review and approve/reject uploaded artworks
- **Featured Content**: Promote high-quality artworks to featured status
- **AI Duplicate Detection**: Monitor and manage duplicate content detection
- **Content Analytics**: Track artwork uploads, views, and engagement

#### 💼 Job & Project Oversight
- **Job Management**: Monitor all job postings and their status
- **Admin Controls**: Close, reopen, or modify jobs as needed
- **Bid Monitoring**: Track all bids and their outcomes
- **Project Analytics**: Monitor job completion rates and success metrics

#### 💳 Financial Management
- **Payment Oversight**: Monitor all transactions and payment flows
- **Refund Processing**: Process refunds for disputed transactions
- **Payment Release**: Control when hire payments are released to artists
- **Revenue Analytics**: Detailed financial reporting and analytics
- **Platform Fee Tracking**: Monitor commission earnings

#### 📊 Analytics & Reporting
- **Real-time Dashboard**: Live platform statistics and metrics
- **Revenue Reports**: Detailed financial reports with date filtering
- **User Growth Analytics**: Track platform growth and user acquisition
- **Performance Metrics**: Monitor platform health and performance

### 🔧 Admin Setup Instructions

#### 1. Create Admin Users
```bash
# Create superuser and sample data
python manage.py setup_admin --create-superuser --create-sample-data

# Create custom admin user
python manage.py setup_admin --create-superuser --admin-username your_admin --admin-email admin@yoursite.com --admin-password secure_password
```

#### 2. Access Admin Interfaces
- **Django Admin Panel**: `http://localhost:8000/admin/`
- **API Dashboard**: `http://localhost:8000/api/admin/dashboard/`
- **Revenue Reports**: `http://localhost:8000/api/admin/revenue-report/`

#### 3. Default Admin Accounts
After running the setup command, these accounts are created:
- **Superuser**: `admin` / `admin123`
- **Admin Manager**: `admin_manager` / `manager123`
- **Content Moderator**: `content_moderator` / `moderator123`

### 🎛️ Admin Dashboard Features

#### Real-time Statistics
- Total users, artists, and buyers
- Revenue tracking and growth metrics
- Active jobs and completed projects
- Artwork statistics and moderation queue
- Recent activity monitoring

#### Quick Actions
- User verification and activation
- Artwork approval and featuring
- Payment processing and refunds
- Job management and closure
- Bulk operations for efficiency

#### Advanced Analytics
- User growth trends over time
- Revenue analysis by payment method
- Platform performance metrics
- Top artists and buyers
- Conversion rate tracking

### 🔐 Admin Security & Permissions

#### Permission Levels
- **Superuser**: Complete system access
- **Admin**: Full platform management capabilities
- **Staff**: Limited administrative functions
- **Content Moderator**: Content review and moderation only

#### Security Features
- Token-based authentication for API access
- Role-based access control
- Audit logging for admin actions
- CSRF protection for web interface
- Rate limiting for API endpoints

---

## 🔐 Authentication

### 1. Register New User
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
    "username": "artist_john",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "user_type": "artist",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+923001234567"
}
```

**Field Details:**
- `username`: Required, unique, 3-150 characters
- `email`: Required, valid email format
- `password`: Required, must pass Django password validation
- `password_confirm`: Required, must match password
- `user_type`: Required, choices: `"artist"` or `"buyer"`
- `first_name`: Required
- `last_name`: Required
- `phone_number`: Optional

**Success Response (201 Created):**
```json
{
    "id": 1,
    "username": "artist_john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "artist",
    "phone_number": "+923001234567",
    "is_verified": false,
    "profile_image": null,
    "created_at": "2025-10-12T10:30:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
    "username": ["A user with that username already exists."],
    "email": ["Enter a valid email address."],
    "password": ["This password is too common."]
}
```

---

### 2. Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "username": "artist_john",
    "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "user": {
        "id": 1,
        "username": "artist_john",
        "email": "john@example.com",
        "user_type": "artist",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

---

### 3. Get User Profile
**Endpoint:** `GET /api/auth/profile/`

**Headers:**
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "username": "artist_john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "artist",
    "phone_number": "+923001234567",
    "is_verified": true,
    "profile_image": "http://localhost:8000/media/profiles/john.jpg",
    "created_at": "2025-10-12T10:30:00Z"
}
```

---

### 4. Update User Profile
**Endpoint:** `PUT /api/auth/profile/` or `PATCH /api/auth/profile/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+923007654321",
    "email": "johnsmith@example.com"
}
```

---

### 5. Logout
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

---

## 🔐 Two-Factor Authentication (2FA)

### Overview
CultureUp supports Time-based One-Time Password (TOTP) two-factor authentication for enhanced account security. Users can enable 2FA using authenticator apps like Google Authenticator, Authy, or Microsoft Authenticator.

### 1. Login with 2FA Support
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response (2FA Disabled - Normal Login):**
```json
{
    "user": {
        "id": 1,
        "username": "user@example.com",
        "user_type": "artist"
    },
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "message": "Login successful"
}
```

**Response (2FA Enabled - Requires Verification):**
```json
{
    "requires_2fa": true,
    "session_token": "temp_session_token_here",
    "message": "Please provide 2FA code"
}
```

---

### 2. Verify 2FA Code
**Endpoint:** `POST /api/auth/2fa/verify/`

**Request Body (with TOTP code):**
```json
{
    "session_token": "temp_session_token_here",
    "totp_code": "123456"
}
```

**Request Body (with backup code):**
```json
{
    "session_token": "temp_session_token_here",
    "backup_code": "ABCD1234"
}
```

**Success Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "user@example.com",
        "user_type": "artist"
    },
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "message": "Login successful"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid TOTP code"
}
```

---

### 3. Setup 2FA
**Endpoint:** `GET /api/auth/2fa/setup/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (New Setup):**
```json
{
    "secret_key": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "message": "Scan QR code with your authenticator app",
    "expires_in_minutes": 30
}
```

**Success Response (Existing Setup):**
```json
{
    "secret_key": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "message": "Existing setup session found. Use the same QR code.",
    "expires_in_minutes": 15
}
```

**Usage:**
1. Call this endpoint to get QR code and secret key
2. **QR code stays the same** for 30 minutes (no need to refresh)
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Or manually enter the secret key in your authenticator app

**Reset Setup (if needed):**
```
POST /api/auth/2fa/reset-setup/
```

---

### 4. Enable 2FA
**Endpoint:** `POST /api/auth/2fa/enable/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Request Body:**
```json
{
    "totp_code": "123456"
}
```

**Success Response (200 OK):**
```json
{
    "message": "2FA enabled successfully",
    "backup_codes": [
        "ABCD1234",
        "EFGH5678",
        "IJKL9012",
        "MNOP3456",
        "QRST7890",
        "UVWX1234",
        "YZAB5678",
        "CDEF9012",
        "GHIJ3456",
        "KLMN7890"
    ]
}
```

**Important:** Save the backup codes in a secure location. Each code can only be used once.

---

### 5. Disable 2FA
**Endpoint:** `POST /api/auth/2fa/disable/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**⚠️ Required: BOTH password AND 2FA verification**

**Request Body (with TOTP code):**
```json
{
    "password": "your_account_password",
    "totp_code": "123456"
}
```

**Request Body (with backup code):**
```json
{
    "password": "your_account_password", 
    "backup_code": "ABCD1234"
}
```

**Success Response (200 OK):**
```json
{
    "message": "2FA disabled successfully"
}
```

**Error Response (Missing TOTP):**
```json
{
    "totp_code": ["Please provide TOTP code from your authenticator app"],
    "backup_code": ["Or provide a backup code instead"],
    "message": "To disable 2FA, you need: 1) Your password AND 2) TOTP code from authenticator app OR backup code"
}
```

**Error Response (Invalid Password):**
```json
{
    "password": ["Invalid password"]
}
```

**Error Response (Invalid TOTP):**
```json
{
    "totp_code": ["Invalid TOTP code. Check your authenticator app."]
}
```

---

### 6. Get 2FA Status
**Endpoint:** `GET /api/auth/2fa/status/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "two_factor_enabled": true,
    "backup_codes_count": 8
}
```

---

### 7. Regenerate Backup Codes
**Endpoint:** `POST /api/auth/2fa/backup-codes/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "backup_codes": [
        "NEW11234",
        "NEW25678",
        "NEW39012",
        "NEW43456",
        "NEW57890",
        "NEW61234",
        "NEW75678",
        "NEW89012",
        "NEW93456",
        "NEW07890"
    ],
    "message": "Backup codes regenerated successfully"
}
```

---

### 2FA Frontend Integration Example

```javascript
// Login flow with 2FA support
const login = async (username, password) => {
    const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (data.requires_2fa) {
        // Show 2FA input form
        return { 
            needs2FA: true, 
            sessionToken: data.session_token 
        };
    } else {
        // Normal login success
        localStorage.setItem('token', data.token);
        return { 
            success: true, 
            user: data.user 
        };
    }
};

// Verify 2FA code
const verify2FA = async (sessionToken, totpCode) => {
    const response = await fetch('/api/auth/2fa/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_token: sessionToken,
            totp_code: totpCode
        })
    });
    
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        return { success: true, user: data.user };
    }
    return { error: data.error };
};

// Setup 2FA
const setup2FA = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/auth/2fa/setup/', {
        headers: { 
            'Authorization': `Token ${token}` 
        }
    });
    
    const data = await response.json();
    if (response.ok) {
        // Display QR code: data.qr_code
        // Show secret key: data.secret_key
        return data;
    }
    return { error: data.error };
};

// Enable 2FA
const enable2FA = async (totpCode) => {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/auth/2fa/enable/', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ totp_code: totpCode })
    });
    
    const data = await response.json();
    if (response.ok) {
        // Save backup codes: data.backup_codes
        return { success: true, backupCodes: data.backup_codes };
    }
    return { error: data.error };
};
```

---

### 2FA Security Best Practices

1. **Backup Codes**: Always save backup codes in a secure location
2. **App Recommendations**: Use Google Authenticator, Authy, or Microsoft Authenticator
3. **Session Timeout**: 2FA sessions expire after 10 minutes
4. **Rate Limiting**: Multiple failed attempts will temporarily lock the account
5. **Recovery**: Use backup codes if you lose access to your authenticator app

---

## 👨‍🎨 Artist Profiles

### 1. List All Artists
**Endpoint:** `GET /api/artist-profiles/`

**Query Parameters:**
- `experience_level`: `beginner`, `intermediate`, or `expert`
- `is_available`: `true` or `false`
- `min_hourly_rate`: Number (e.g., `50`)
- `max_hourly_rate`: Number (e.g., `200`)
- `search`: Search keyword
- `ordering`: `rating`, `-rating`, `hourly_rate`, `-hourly_rate`
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Example Request:**
```
GET /api/artist-profiles/?experience_level=expert&is_available=true&min_hourly_rate=100&ordering=-rating&page=1
```

**Success Response (200 OK):**
```json
{
    "count": 45,
    "next": "http://localhost:8000/api/artist-profiles/?page=2",
    "previous": null,
    "results": [
        {
            "user": {
                "id": 1,
                "username": "artist_john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "user_type": "artist",
                "phone_number": "+923001234567",
                "is_verified": true,
                "profile_image": "http://localhost:8000/media/profiles/john.jpg",
                "created_at": "2025-10-12T10:30:00Z"
            },
            "bio": "Professional digital artist with 10 years of experience",
            "skills": "Digital Art, Illustration, 3D Modeling",
            "experience_level": "expert",
            "hourly_rate": "150.00",
            "portfolio_description": "Specialized in character design and concept art",
            "rating": 4.8,
            "total_projects_completed": 120,
            "total_earnings": "45000.00",
            "is_available": true,
            "completion_rate": 98.5,
            "total_reviews": 85
        }
    ]
}
```

---

### 2. Get Artist Details
**Endpoint:** `GET /api/artist-profiles/{id}/`

**Example:** `GET /api/artist-profiles/1/`

---

### 3. Create Artist Profile
**Endpoint:** `POST /api/artist-profiles/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "bio": "Professional digital artist specializing in fantasy art",
    "skills": "Digital Painting, Character Design, Concept Art",
    "experience_level": "expert",
    "hourly_rate": "150.00",
    "portfolio_description": "10+ years creating stunning fantasy artwork for games and books",
    "is_available": true
}
```

**Field Details:**
- `bio`: Optional, max 1000 characters
- `skills`: Optional, comma-separated skills
- `experience_level`: Required, choices: `"beginner"`, `"intermediate"`, `"expert"`
- `hourly_rate`: Required, decimal (max 2 decimal places)
- `portfolio_description`: Optional, max 2000 characters
- `is_available`: Optional, boolean (default: true)

---

### 4. Update Artist Profile
**Endpoint:** `PUT /api/artist-profiles/{id}/` or `PATCH /api/artist-profiles/{id}/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Request Body (PATCH - partial update):**
```json
{
    "hourly_rate": "175.00",
    "is_available": false
}
```
**Request Body (PATCH - full update):**

```json
{
    "bio": "Experienced digital artist specializing in portraits.",
    "skills": "Digital Painting, Concept Art, Illustration",
    "experience_level": "Intermediate",
    "hourly_rate": "200.00",
    "portfolio_description": "Over 100 commissioned artworks completed.",
    "is_available": true
}

```

---


### 5. Get Artist Reviews
**Endpoint:** `GET /api/artist-profiles/{id}/reviews/`

**Example:** `GET /api/artist-profiles/1/reviews/`

---

### 6. Get Artist Artworks
**Endpoint:** `GET /api/artist-profiles/{id}/artworks/`

**Example:** `GET /api/artist-profiles/1/artworks/`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "artist": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "title": "Dreamscape",
      "description": "A surreal digital painting exploring abstract imagination.",
      "category": {
        "id": 2,
        "name": "Digital Art"
      },
      "artwork_type": "digital",
      "price": "250.00",
      "image": "http://127.0.0.1:8000/media/artworks/dreamscape.jpg",
      "watermarked_image": null,
      "is_available": true,
      "is_featured": true,
      "views_count": 145,
      "likes_count": 30,
      "created_at": "2025-10-16T12:00:00Z",
      "updated_at": "2025-10-18T18:45:00Z"
    },
    {
      "id": 13,
      "artist": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "title": "Serenity",
      "description": "A minimalistic landscape inspired by nature’s calmness.",
      "category": {
        "id": 3,
        "name": "Nature"
      },
      "artwork_type": "physical",
      "price": "480.00",
      "image": "http://127.0.0.1:8000/media/artworks/serenity.jpg",
      "watermarked_image": null,
      "is_available": true,
      "is_featured": false,
      "views_count": 92,
      "likes_count": 20,
      "created_at": "2025-10-18T15:10:00Z",
      "updated_at": "2025-10-19T09:00:00Z"
    }
  ]
}


```



---

## 🛍️ Buyer Profiles

### 1. List All Buyers
**Endpoint:** `GET /api/buyer-profiles/`

**Query Parameters:**
- `search`: Search keyword
- `ordering`: `total_spent`, `-total_spent`, `projects_posted`, `-projects_posted`
- `page`: Page number
- `page_size`: Items per page

**Success Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/buyer-profiles/?page=2",
    "previous": null,
    "results": [
        {
            "user": {
                "id": 21,
                "username": "buyer_sarah",
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "user_type": "buyer",
                "phone_number": "+923001234567",
                "is_verified": true,
                "profile_image": "http://localhost:8000/media/profiles/sarah.jpg",
                "created_at": "2025-10-12T10:30:00Z"
            },
            "company_name": "Tech Innovations Inc",
            "address": "123 Main Street, Lahore, Pakistan",
            "total_spent": "15000.00",
            "projects_posted": 12
        }
    ]
}
```

---

### 2. Get Buyer Details
**Endpoint:** `GET /api/buyer-profiles/{user_id}/`

**Example:** `GET /api/buyer-profiles/21/`

**Success Response (200 OK):**
```json
{
    "user": {
        "id": 21,
        "username": "buyer_sarah",
        "email": "sarah@example.com",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "user_type": "buyer",
        "phone_number": "+923001234567",
        "is_verified": true,
        "profile_image": "http://localhost:8000/media/profiles/sarah.jpg",
        "created_at": "2025-10-12T10:30:00Z"
    },
    "company_name": "Tech Innovations Inc",
    "address": "123 Main Street, Lahore, Pakistan",
    "total_spent": "15000.00",
    "projects_posted": 12
}
```

---

### 3. Get Buyer Purchases (🆕 NEW)
**Endpoint:** `GET /api/buyer-profiles/{user_id}/purchases/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Example:** `GET /api/buyer-profiles/21/purchases/`

**Success Response (200 OK):**
```json
{
    "orders": [
        {
            "id": 1,
            "buyer": {
                "id": 21,
                "username": "buyer_sarah"
            },
            "order_type": "artwork",
            "status": "completed",
            "total_amount": "599.98",
            "shipping_address": "123 Main Street, Lahore, Pakistan",
            "created_at": "2025-10-10T14:30:00Z",
            "updated_at": "2025-10-12T16:45:00Z",
            "artwork_items": [
                {
                    "id": 1,
                    "artwork": 5,
                    "artwork_title": "Digital Portrait",
                    "artwork_artist": "artist_john",
                    "quantity": 1,
                    "price": "299.99",
                    "total_price": "299.99"
                },
                {
                    "id": 2,
                    "artwork": 8,
                    "artwork_title": "Abstract Landscape",
                    "artwork_artist": "artist_jane",
                    "quantity": 1,
                    "price": "299.99",
                    "total_price": "299.99"
                }
            ],
            "equipment_items": []
        }
    ],
    "payments": [
        {
            "id": 3,
            "payer": {
                "id": 21,
                "username": "buyer_sarah"
            },
            "payee": {
                "id": 1,
                "username": "artist_john",
                "first_name": "John",
                "last_name": "Doe"
            },
            "order": null,
            "job": {
                "id": 5,
                "title": "Logo Design for Tech Startup"
            },
            "amount": "850.00",
            "payment_method": "stripe",
            "status": "completed",
            "transaction_id": "TXN789456123",
            "created_at": "2025-10-08T11:20:00Z",
            "platform_fee": "85.00",
            "artist_earning": "765.00"
        }
    ],
    "total_orders": 3,
    "total_payments": 5,
    "completed_orders": 2,
    "completed_payments": 4
}
```

**Purchase Types Explained:**
- **Orders**: Purchases of artworks and equipment from the marketplace
- **Payments**: Payments made to artists for custom job/project work

---

### 4. Create Buyer Profile
**Endpoint:** `POST /api/buyer-profiles/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "company_name": "Tech Innovations Inc",
    "address": "123 Main Street, Lahore, Pakistan"
}
```

**Field Details:**
- `company_name`: Optional, max 200 characters
- `address`: Optional, max 500 characters

---

### 5. Update Buyer Profile
**Endpoint:** `PATCH /api/buyer-profiles/{id}/`

**Request Body:**
```json
{
    "company_name": "Tech Innovations Private Ltd",
    "address": "456 New Street, Karachi, Pakistan"
}
```

---

## 🎨 Artworks (with S3 & Rekognition Integration)

**🆕 Now with automatic S3 storage and AI duplicate detection!**

### 1. List All Artworks
**Endpoint:** `GET /api/artworks/`

**Query Parameters:**
- `category`: Category ID (e.g., `1`)
- `artwork_type`: `digital`, `physical`, or `mixed`
- `min_price`: Minimum price (e.g., `100`)
- `max_price`: Maximum price (e.g., `1000`)
- `is_featured`: `true` or `false`
- `search`: Search in title and description
- `ordering`: `price`, `-price`, `created_at`, `-created_at`, `views_count`, `-views_count`, `likes_count`, `-likes_count`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/artworks/?category=1&artwork_type=digital&min_price=100&max_price=500&is_featured=true&ordering=-likes_count
```

**Success Response (200 OK):**
```json
{
    "count": 234,
    "next": "http://localhost:8000/api/artworks/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "artist": {
                "id": 1,
                "username": "artist_john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "user_type": "artist"
            },
            "title": "Sunset Over Mountains",
            "description": "A beautiful digital painting of a sunset",
            "category": {
                "id": 1,
                "name": "Digital Art",
                "description": "Digital artwork category"
            },
            "artwork_type": "digital",
            "price": "299.99",
            "image": "http://localhost:8000/media/artworks/sunset.jpg",
            "watermarked_image": "http://localhost:8000/media/artworks/sunset_wm.jpg",
            "is_available": true,
            "is_featured": true,
            "views_count": 1250,
            "likes_count": 89,
            "created_at": "2025-10-10T15:30:00Z",
            "updated_at": "2025-10-12T09:15:00Z"
        }
    ]
}
```

---

### 2. Get Artwork Details
**Endpoint:** `GET /api/artworks/{id}/`

**Example:** `GET /api/artworks/1/`

---

### 3. Create Artwork (🆕 with S3 & Duplicate Detection)
**Endpoint:** `POST /api/artworks/`

**Headers:**
```
Authorization: Token YOUR_ARTIST_TOKEN
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
title: "Sunset Over Mountains"
description: "A beautiful digital painting capturing the serene beauty of sunset"
category_id: 1
artwork_type: "digital"
price: 299.99
image: [file upload]
is_available: true
is_featured: false
```

**Field Details:**
- `title`: Required, max 200 characters
- `description`: Required
- `category_id`: Required, valid category ID
- `artwork_type`: Required, choices: `"digital"`, `"physical"`, `"mixed"`
- `price`: Required, decimal (max 2 decimal places)
- `image`: Required, image file (jpg, png, gif)
- `is_available`: Optional, boolean (default: true)
- `is_featured`: Optional, boolean (default: false)

**🆕 What Happens Automatically:**
1. ✅ Image uploaded to AWS S3 (cloud storage)
2. ✅ AI checks for duplicate artworks using AWS Rekognition
3. ✅ Watermark generated and uploaded to S3
4. ✅ Rekognition labels detected (e.g., "Art", "Painting", "Digital")

**Success Response (201 Created):**
```json
{
  "message": "Artwork uploaded successfully",
  "artwork": {
    "id": 1,
    "artist": {
      "id": 1,
      "username": "artist_john"
    },
    "title": "Sunset Over Mountains",
    "description": "A beautiful digital painting...",
    "category": {
      "id": 1,
      "name": "Digital Art"
    },
    "artwork_type": "digital",
    "price": "299.99",
    "s3_image_url": "https://bucket.s3.amazonaws.com/artworks/1/uuid.jpg",
    "s3_watermarked_url": "https://bucket.s3.amazonaws.com/artworks/1/watermarked_uuid.jpg",
    "rekognition_checked": true,
    "rekognition_labels": [
      {"name": "Art", "confidence": 99.5},
      {"name": "Painting", "confidence": 98.2},
      {"name": "Sunset", "confidence": 95.0}
    ],
    "similarity_score": "0.00",
    "is_available": true,
    "is_featured": false,
    "views_count": 0,
    "likes_count": 0,
    "created_at": "2025-10-12T10:30:00Z"
  },
  "duplicate_check": {
    "checked": true,
    "total_compared": 10,
    "duplicate_found": false
  },
  "rekognition_labels": [
    {"name": "Art", "confidence": 99.5},
    {"name": "Painting", "confidence": 98.2}
  ]
}
```

**🚫 Duplicate Detected Response (400 Bad Request):**
```json
{
  "error": "Duplicate artwork detected",
  "message": "This artwork is too similar to an existing artwork in our system",
  "duplicate_detected": true,
  "similarity_score": 92.5,
  "matched_artwork": {
    "id": 5,
    "title": "Similar Artwork",
    "artist": "john_doe"
  }
}
```

**How Duplicate Detection Works:**
- **Label Detection (60%)**: AI identifies objects/scenes (e.g., "Portrait", "Landscape")
- **Face Comparison (40%)**: Compares faces in portraits
- **Combined Score**: If ≥ 85% similar → Rejected as duplicate
- **Same Artist**: Allowed to upload variations of their own work

---

### 4. Update Artwork (🆕 with S3 Support)
**Endpoint:** `PATCH /api/artworks/{id}/` or `PUT /api/artworks/{id}/`

**Headers:**
```
Authorization: Token YOUR_ARTIST_TOKEN
Content-Type: multipart/form-data
```

**Request Body (to update text fields only):**
```json
{
    "price": "349.99",
    "is_available": true,
    "description": "Updated description"
}
```

**Request Body (to update image):**
```
image: [new file upload]
title: "Updated Title"
price: 349.99
```

**🆕 What Happens When Updating Image:**
1. ✅ Old image deleted from S3
2. ✅ New image uploaded to S3
3. ✅ Duplicate check runs again
4. ✅ New watermark generated
5. ✅ New Rekognition labels detected

**Note:** Only the artwork owner (artist) can update their artwork.

---

### 5. Like Artwork
**Endpoint:** `POST /api/artworks/{id}/like/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Artwork liked successfully",
    "likes_count": 90
}
```

---

### 6. Get Featured Artworks
**Endpoint:** `GET /api/artworks/featured/`

---

## 💼 Jobs/Projects

### 1. List All Jobs
**Endpoint:** `GET /api/jobs/`

**Query Parameters:**
- `status`: `open`, `in_progress`, `completed`, or `cancelled`
- `category`: Category ID
- `experience_level`: `entry`, `intermediate`, or `expert`
- `min_budget`: Minimum budget
- `max_budget`: Maximum budget
- `search`: Search in title and description
- `ordering`: `budget_min`, `-budget_min`, `deadline`, `-deadline`, `created_at`, `-created_at`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/jobs/?status=open&category=1&experience_level=expert&min_budget=500&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 78,
    "next": "http://localhost:8000/api/jobs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 5,
            "buyer": {
                "id": 2,
                "username": "buyer_sarah",
                "email": "sarah@example.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "user_type": "buyer"
            },
            "title": "Logo Design for Tech Startup",
            "description": "Need a modern, minimalist logo design for a tech startup...",
            "category": {
                "id": 2,
                "name": "Graphic Design",
                "description": "Graphic design category"
            },
            "budget_min": "500.00",
            "budget_max": "1000.00",
            "duration_days": 7,
            "required_skills": "Logo Design, Branding, Adobe Illustrator",
            "experience_level": "expert",
            "status": "open",
            "hired_artist": null,
            "final_amount": null,
            "deadline": "2025-10-20T23:59:59Z",
            "created_at": "2025-10-12T08:00:00Z",
            "updated_at": "2025-10-12T08:00:00Z",
            "average_bid": 725.50,
            "total_bids": 8,
            "deadline_approaching": false
        }
    ]
}
```

---

### 2. Get Job Details
**Endpoint:** `GET /api/jobs/{id}/`

**Example:** `GET /api/jobs/5/`

---

### 3. Create Job
**Endpoint:** `POST /api/jobs/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "Logo Design for Tech Startup",
    "description": "I need a modern, minimalist logo design for my tech startup. The logo should convey innovation and reliability.",
    "category_id": 2,
    "budget_min": "500.00",
    "budget_max": "1000.00",
    "duration_days": 7,
    "required_skills": "Logo Design, Branding, Adobe Illustrator",
    "experience_level": "expert",
    "deadline": "2025-10-20T23:59:59Z"
}
```

**Field Details:**
- `title`: Required, max 200 characters
- `description`: Required
- `category_id`: Required, valid category ID
- `budget_min`: Required, decimal
- `budget_max`: Required, decimal (must be >= budget_min)
- `duration_days`: Required, positive integer
- `required_skills`: Optional, comma-separated skills
- `experience_level`: Required, choices: `"entry"`, `"intermediate"`, `"expert"`
- `deadline`: Required, ISO 8601 datetime format

**Success Response (201 Created):**
```json
{
    "id": 5,
    "buyer": {
        "id": 2,
        "username": "buyer_sarah"
    },
    "title": "Logo Design for Tech Startup",
    "description": "I need a modern, minimalist logo...",
    "category": {
        "id": 2,
        "name": "Graphic Design"
    },
    "budget_min": "500.00",
    "budget_max": "1000.00",
    "duration_days": 7,
    "required_skills": "Logo Design, Branding, Adobe Illustrator",
    "experience_level": "expert",
    "status": "open",
    "hired_artist": null,
    "final_amount": null,
    "deadline": "2025-10-20T23:59:59Z",
    "created_at": "2025-10-12T08:00:00Z",
    "average_bid": null,
    "total_bids": 0,
    "deadline_approaching": false
}
```

---

### 4. Update Job
**Endpoint:** `PATCH /api/jobs/{id}/`

**Request Body:**
```json
{
    "budget_max": "1200.00",
    "deadline": "2025-10-25T23:59:59Z"
}
```

---

### 5. Get Job Bids
**Endpoint:** `GET /api/jobs/{id}/bids/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Example:** `GET /api/jobs/5/bids/`

---

### 6. Hire Artist
**Endpoint:** `POST /api/jobs/{id}/hire/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "bid_id": 12,
    "final_amount": "850.00"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Artist hired successfully",
    "job": {
        "id": 5,
        "status": "in_progress",
        "hired_artist": {
            "id": 1,
            "username": "artist_john"
        },
        "final_amount": "850.00"
    }
}
```

---

### 7. Complete Job
**Endpoint:** `POST /api/jobs/{id}/complete/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Job completed successfully",
    "job": {
        "id": 5,
        "status": "completed"
    }
}
```

---

## 💰 Bids

### 1. List My Bids
**Endpoint:** `GET /api/bids/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `status`: `pending`, `accepted`, or `rejected`
- `ordering`: `bid_amount`, `-bid_amount`, `delivery_time`, `-delivery_time`, `created_at`, `-created_at`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/bids/?status=pending&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 12,
            "job": {
                "id": 5,
                "title": "Logo Design for Tech Startup",
                "buyer_name": "buyer_sarah",
                "category_name": "Graphic Design",
                "budget_min": "500.00",
                "budget_max": "1000.00",
                "status": "open"
            },
            "artist": {
                "id": 1,
                "username": "artist_john"
            },
            "bid_amount": "750.00",
            "delivery_time": 5,
            "cover_letter": "I have extensive experience in logo design...",
            "status": "pending",
            "created_at": "2025-10-12T09:30:00Z",
            "bid_rank": 3
        }
    ]
}
```

---

### 2. Get Bid Details
**Endpoint:** `GET /api/bids/{id}/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

---

### 3. Create Bid
**Endpoint:** `POST /api/bids/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "job_id": 5,
    "bid_amount": "750.00",
    "delivery_time": 5,
    "cover_letter": "I have over 10 years of experience in logo design and branding. I've created logos for 50+ tech startups. I understand your need for a modern, minimalist design and can deliver exactly what you're looking for. Please check my portfolio for similar work."
}
```

**Field Details:**
- `job_id`: Required, valid job ID
- `bid_amount`: Required, decimal (should be within job's budget range)
- `delivery_time`: Required, positive integer (days)
- `cover_letter`: Required, max 2000 characters

**Success Response (201 Created):**
```json
{
    "id": 12,
    "job": {
        "id": 5,
        "title": "Logo Design for Tech Startup"
    },
    "artist": {
        "id": 1,
        "username": "artist_john"
    },
    "bid_amount": "750.00",
    "delivery_time": 5,
    "cover_letter": "I have over 10 years of experience...",
    "status": "pending",
    "created_at": "2025-10-12T09:30:00Z",
    "bid_rank": 3
}
```

---

### 4. Update Bid
**Endpoint:** `PATCH /api/bids/{id}/`

**Request Body:**
```json
{
    "bid_amount": "725.00",
    "delivery_time": 6
}
```

---

### 5. Delete Bid
**Endpoint:** `DELETE /api/bids/{id}/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (204 No Content)**

---

## 📦 Orders

### 1. List My Orders
**Endpoint:** `GET /api/orders/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `order_type`: `artwork` or `equipment`
- `status`: `pending`, `confirmed`, `shipped`, `delivered`, or `cancelled`
- `ordering`: `created_at`, `-created_at`, `total_amount`, `-total_amount`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/orders/?order_type=artwork&status=confirmed&ordering=-created_at
```

---

### 2. Get Order Details
**Endpoint:** `GET /api/orders/{id}/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

---

### 3. Create Order
**Endpoint:** `POST /api/orders/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body (Artwork Order):**
```json
{
    "order_type": "artwork",
    "shipping_address": "123 Main Street, Gulberg, Lahore, Pakistan",
    "artwork_items": [
        {
            "artwork_id": 1,
            "quantity": 1
        },
        {
            "artwork_id": 3,
            "quantity": 2
        }
    ]
}
```

**Request Body (Equipment Order):**
```json
{
    "order_type": "equipment",
    "shipping_address": "456 Art Street, DHA, Karachi, Pakistan",
    "equipment_items": [
        {
            "equipment_id": 5,
            "quantity": 3
        },
        {
            "equipment_id": 8,
            "quantity": 1
        }
    ]
}
```

**Request Body (Mixed Order):**
```json
{
    "order_type": "equipment",
    "shipping_address": "789 Creative Avenue, Islamabad, Pakistan",
    "artwork_items": [
        {
            "artwork_id": 2,
            "quantity": 1
        }
    ],
    "equipment_items": [
        {
            "equipment_id": 5,
            "quantity": 2
        }
    ]
}
```

**Field Details:**
- `order_type`: Required, choices: `"artwork"` or `"equipment"`
- `shipping_address`: Required, max 500 characters
- `artwork_items`: List of artwork items (required if order_type is artwork)
  - `artwork_id`: Required, valid artwork ID
  - `quantity`: Optional, default 1
- `equipment_items`: List of equipment items
  - `equipment_id`: Required, valid equipment ID
  - `quantity`: Optional, default 1

**Success Response (201 Created):**
```json
{
    "id": 1,
    "buyer": {
        "id": 2,
        "username": "buyer_sarah"
    },
    "order_type": "artwork",
    "status": "pending",
    "total_amount": "899.97",
    "shipping_address": "123 Main Street, Gulberg, Lahore, Pakistan",
    "created_at": "2025-10-12T10:00:00Z",
    "updated_at": "2025-10-12T10:00:00Z",
    "artwork_items": [
        {
            "id": 1,
            "artwork": 1,
            "artwork_title": "Sunset Over Mountains",
            "artwork_artist": "artist_john",
            "quantity": 1,
            "price": "299.99",
            "total_price": "299.99"
        },
        {
            "id": 2,
            "artwork": 3,
            "artwork_title": "Ocean Waves",
            "artwork_artist": "artist_jane",
            "quantity": 2,
            "price": "299.99",
            "total_price": "599.98"
        }
    ],
    "equipment_items": []
}
```

---

### 4. Confirm Order
**Endpoint:** `POST /api/orders/{id}/confirm/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Order confirmed successfully",
    "order": {
        "id": 1,
        "status": "confirmed"
    }
}
```

---

### 5. Cancel Order
**Endpoint:** `POST /api/orders/{id}/cancel/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

---

## 💳 Payments

### 1. List My Payments
**Endpoint:** `GET /api/payments/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `payment_method`: `jazzcash`, `bank_transfer`, or `cash_on_delivery`
- `status`: `pending`, `completed`, `failed`, or `refunded`
- `ordering`: `created_at`, `-created_at`, `amount`, `-amount`
- `page`: Page number
- `page_size`: Items per page

---

### 2. Create Payment
**Endpoint:** `POST /api/payments/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body (Order Payment):**
```json
{
    "payee": 1,
    "order": 1,
    "amount": "899.97",
    "payment_method": "jazzcash"
}
```

**Request Body (Job Payment):**
```json
{
    "payee": 1,
    "job": 5,
    "amount": "850.00",
    "payment_method": "bank_transfer"
}
```

**Field Details:**
- `payee`: Required, user ID of the receiver
- `order`: Optional, order ID (for order payments)
- `job`: Optional, job ID (for job payments)
- `amount`: Required, decimal
- `payment_method`: Required, choices: `"jazzcash"`, `"bank_transfer"`, `"cash_on_delivery"`

**Success Response (201 Created):**
```json
{
    "id": 1,
    "payer": {
        "id": 2,
        "username": "buyer_sarah"
    },
    "payee": {
        "id": 1,
        "username": "artist_john"
    },
    "order": 1,
    "job": null,
    "amount": "899.97",
    "payment_method": "jazzcash",
    "status": "pending",
    "transaction_id": "TXN123456789",
    "created_at": "2025-10-12T10:15:00Z",
    "platform_fee": "89.997",
    "artist_earning": "809.973"
}
```

---

### 3. Process Payment with Stripe (3D Secure Enabled)
**Endpoint:** `POST /api/payments/{id}/process/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
    "client_secret": "pi_1234567890_secret_abcdef",
    "payment_intent_id": "pi_1234567890",
    "requires_action": false,
    "message": "Stripe PaymentIntent created successfully. Complete 3D Secure if required."
}
```

---

### 4. Confirm Payment (After 3D Secure)
**Endpoint:** `POST /api/payments/{id}/confirm/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "payment_method_id": "pm_1234567890",
    "return_url": "https://your-website.com/return"
}
```

**Response (Requires 3D Secure):**
```json
{
    "requires_action": true,
    "client_secret": "pi_1234567890_secret_abcdef",
    "next_action": {
        "type": "use_stripe_sdk"
    },
    "message": "Please complete 3D Secure verification"
}
```

**Response (Payment Successful):**
```json
{
    "success": true,
    "payment_id": 1,
    "transaction_id": "TXN123456789",
    "status": "completed",
    "message": "Payment completed successfully"
}
```

---

### 5. Handle 3D Secure Completion
**Endpoint:** `POST /api/payments/{id}/3d-secure/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response:**
```json
{
    "success": true,
    "payment_id": 1,
    "transaction_id": "TXN123456789",
    "status": "completed",
    "message": "3D Secure verification completed successfully"
}
```

---

### Stripe 3D Secure Payment Flow

#### Frontend Integration Example:

```javascript
// Complete Stripe payment flow with 3D Secure
const processStripePayment = async (paymentId, cardElement) => {
    const stripe = Stripe('pk_test_your_publishable_key');
    
    try {
        // Step 1: Process payment to get client_secret
        const processResponse = await fetch(`/api/payments/${paymentId}/process/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const processData = await processResponse.json();
        
        // Step 2: Create payment method
        const { paymentMethod, error: pmError } = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
        });
        
        if (pmError) {
            throw new Error(pmError.message);
        }
        
        // Step 3: Confirm payment
        const confirmResponse = await fetch(`/api/payments/${paymentId}/confirm/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                payment_method_id: paymentMethod.id,
                return_url: window.location.origin + '/payment-return'
            })
        });
        
        const confirmData = await confirmResponse.json();
        
        // Step 4: Handle 3D Secure if required
        if (confirmData.requires_action) {
            const { error: confirmError } = await stripe.confirmCardPayment(
                confirmData.client_secret
            );
            
            if (confirmError) {
                throw new Error(confirmError.message);
            }
            
            // Step 5: Check final status
            const finalResponse = await fetch(`/api/payments/${paymentId}/3d-secure/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`
                }
            });
            
            return await finalResponse.json();
        } else {
            // Payment completed without 3D Secure
            return confirmData;
        }
        
    } catch (error) {
        console.error('Payment failed:', error);
        throw error;
    }
};

// Usage
try {
    const result = await processStripePayment(123, cardElement);
    console.log('Payment successful:', result);
} catch (error) {
    console.error('Payment failed:', error.message);
}
```

#### Key Features:
- **3D Secure (SCA)**: Automatic OTP verification through user's bank
- **PKR Currency**: Payments processed in Pakistani Rupees
- **Manual Confirmation**: Frontend controls the payment flow
- **Error Handling**: Comprehensive error responses
- **Security**: Bank-level OTP verification


---



## 💬 Messages

### 1. List My Messages
**Endpoint:** `GET /api/messages/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `is_read`: `true` or `false`
- `job`: Job ID
- `ordering`: `created_at`, `-created_at`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/messages/?is_read=false&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "sender": {
                "id": 2,
                "username": "buyer_sarah",
                "first_name": "Sarah",
                "last_name": "Johnson"
            },
            "receiver": {
                "id": 1,
                "username": "artist_john",
                "first_name": "John",
                "last_name": "Doe"
            },
            "job": 5,
            "content": "Hi John, I really liked your bid on my logo design project. Can we discuss the timeline?",
            "attachment": null,
            "is_read": false,
            "created_at": "2025-10-12T11:30:00Z"
        }
    ]
}
```

---

### 2. Send Message
**Endpoint:** `POST /api/messages/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
receiver_id: 1
job: 5
content: "Hi, I'm interested in your project. Can we discuss the requirements in detail?"
attachment: [file upload - optional]
```

**Field Details:**
- `receiver_id`: Required, user ID of the receiver
- `job`: Optional, job ID (for job-related messages)
- `content`: Required, max 2000 characters
- `attachment`: Optional, file upload

**Success Response (201 Created):**
```json
{
    "id": 2,
    "sender": {
        "id": 1,
        "username": "artist_john"
    },
    "receiver": {
        "id": 2,
        "username": "buyer_sarah"
    },
    "job": 5,
    "content": "Hi, I'm interested in your project...",
    "attachment": null,
    "is_read": false,
    "created_at": "2025-10-12T11:45:00Z"
}
```

---

### 3. Mark Message as Read
**Endpoint:** `POST /api/messages/{id}/mark-read/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Message marked as read",
    "message_id": 1,
    "is_read": true
}
```

---

### 4. Get Conversations
**Endpoint:** `GET /api/messages/conversations/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "conversations": [
        {
            "user": {
                "id": 2,
                "username": "buyer_sarah",
                "first_name": "Sarah",
                "profile_image": "http://localhost:8000/media/profiles/sarah.jpg"
            },
            "last_message": {
                "id": 5,
                "content": "Great! Let's finalize the details.",
                "created_at": "2025-10-12T14:00:00Z",
                "is_read": true
            },
            "unread_count": 0
        },
        {
            "user": {
                "id": 3,
                "username": "buyer_mike",
                "first_name": "Mike",
                "profile_image": null
            },
            "last_message": {
                "id": 3,
                "content": "When can you start the project?",
                "created_at": "2025-10-12T10:30:00Z",
                "is_read": false
            },
            "unread_count": 2
        }
    ]
}
```

---

## ⭐ Reviews

### 1. List Reviews
**Endpoint:** `GET /api/reviews/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `rating`: `1`, `2`, `3`, `4`, or `5`
- `ordering`: `created_at`, `-created_at`, `rating`, `-rating`
- `page`: Page number
- `page_size`: Items per page

---

### 2. Create Review
**Endpoint:** `POST /api/reviews/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "job": 5,
    "rating": 5,
    "comment": "Excellent work! John delivered the logo on time and it exceeded my expectations. Very professional and responsive to feedback. Highly recommended!"
}
```

**Field Details:**
- `job`: Required, job ID (must be completed job)
- `rating`: Required, integer between 1-5
- `comment`: Required, max 1000 characters

**Success Response (201 Created):**
```json
{
    "id": 1,
    "reviewer": {
        "id": 2,
        "username": "buyer_sarah",
        "first_name": "Sarah",
        "last_name": "Johnson"
    },
    "artist": {
        "id": 1,
        "username": "artist_john",
        "first_name": "John",
        "last_name": "Doe"
    },
    "job": {
        "id": 5,
        "title": "Logo Design for Tech Startup"
    },
    "rating": 5,
    "comment": "Excellent work! John delivered the logo...",
    "created_at": "2025-10-12T15:00:00Z"
}
```

---

### 3. Update Review
**Endpoint:** `PATCH /api/reviews/{id}/`

**Request Body:**
```json
{
    "rating": 4,
    "comment": "Good work overall. Minor revisions needed but delivered on time."
}
```

---

### 4. Delete Review
**Endpoint:** `DELETE /api/reviews/{id}/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (204 No Content)**

---

## 📄 Contracts

### 1. List My Contracts
**Endpoint:** `GET /api/contracts/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `status`: `draft`, `pending`, `active`, `completed`, or `terminated`
- `rights_type`: `display_only`, `reproduction`, `commercial`, or `exclusive`
- `ordering`: `created_at`, `-created_at`, `amount`, `-amount`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/contracts/?status=active&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "job": {
                "id": 5,
                "title": "Logo Design for Tech Startup"
            },
            "artist": {
                "id": 1,
                "username": "artist_john"
            },
            "buyer": {
                "id": 2,
                "username": "buyer_sarah"
            },
            "terms": "The artist will create a unique logo design with 3 revision rounds. Final files will be delivered in AI, PNG, and SVG formats.",
            "rights_type": "exclusive",
            "amount": "850.00",
            "deadline": "2025-10-20T23:59:59Z",
            "status": "active",
            "artist_signed": true,
            "buyer_signed": true,
            "artist_signed_at": "2025-10-12T12:00:00Z",
            "buyer_signed_at": "2025-10-12T13:00:00Z",
            "created_at": "2025-10-12T11:00:00Z",
            "is_fully_signed": true
        }
    ]
}
```

---

### 2. Create Contract
**Endpoint:** `POST /api/contracts/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "job": 5,
    "artist": 1,
    "terms": "The artist will create a unique logo design with 3 revision rounds. Final files will be delivered in AI, PNG, and SVG formats. The buyer will have exclusive rights to use the logo.",
    "rights_type": "exclusive",
    "amount": "850.00",
    "deadline": "2025-10-20T23:59:59Z"
}
```

**Field Details:**
- `job`: Required, job ID
- `artist`: Required, artist user ID
- `terms`: Required, contract terms and conditions
- `rights_type`: Required, choices: `"display_only"`, `"reproduction"`, `"commercial"`, `"exclusive"`
- `amount`: Required, decimal
- `deadline`: Required, ISO 8601 datetime format

**Success Response (201 Created):**
```json
{
    "id": 1,
    "job": {
        "id": 5,
        "title": "Logo Design for Tech Startup"
    },
    "artist": {
        "id": 1,
        "username": "artist_john"
    },
    "buyer": {
        "id": 2,
        "username": "buyer_sarah"
    },
    "terms": "The artist will create a unique logo design...",
    "rights_type": "exclusive",
    "amount": "850.00",
    "deadline": "2025-10-20T23:59:59Z",
    "status": "pending",
    "artist_signed": false,
    "buyer_signed": false,
    "artist_signed_at": null,
    "buyer_signed_at": null,
    "created_at": "2025-10-12T11:00:00Z",
    "is_fully_signed": false
}
```

---

### 3. Sign Contract
**Endpoint:** `POST /api/contracts/{id}/sign/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Contract signed successfully",
    "contract": {
        "id": 1,
        "artist_signed": true,
        "buyer_signed": false,
        "artist_signed_at": "2025-10-12T12:00:00Z",
        "is_fully_signed": false,
        "status": "pending"
    }
}
```

---

## 🔔 Notifications

### 1. List My Notifications
**Endpoint:** `GET /api/notifications/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `notification_type`: `new_bid`, `bid_accepted`, `job_completed`, `payment_received`, `new_message`, `contract_signed`
- `is_read`: `true` or `false`
- `ordering`: `created_at`, `-created_at`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/notifications/?is_read=false&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "notification_type": "new_bid",
            "title": "New Bid Received",
            "message": "You received a new bid from artist_john on your job 'Logo Design for Tech Startup'",
            "is_read": false,
            "created_at": "2025-10-12T09:30:00Z"
        },
        {
            "id": 2,
            "notification_type": "new_message",
            "title": "New Message",
            "message": "You have a new message from buyer_sarah",
            "is_read": false,
            "created_at": "2025-10-12T11:30:00Z"
        }
    ]
}
```

---

### 2. Mark Notification as Read
**Endpoint:** `POST /api/notifications/{id}/mark-read/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Notification marked as read",
    "notification_id": 1,
    "is_read": true
}
```

---

### 3. Mark All Notifications as Read
**Endpoint:** `POST /api/notifications/mark-all-read/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "All notifications marked as read",
    "count": 8
}
```

---

### 4. Get Unread Count
**Endpoint:** `GET /api/notifications/unread-count/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK):**
```json
{
    "unread_count": 8
}
```

---

## 🛠️ Equipment

### 1. List All Equipment
**Endpoint:** `GET /api/equipment/`

**Query Parameters:**
- `equipment_type`: `frame`, `paint`, `brush`, `canvas`, or `other`
- `min_price`: Minimum price
- `max_price`: Maximum price
- `in_stock`: `true` or `false`
- `search`: Search keyword
- `ordering`: `price`, `-price`, `stock_quantity`, `-stock_quantity`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/equipment/?equipment_type=brush&in_stock=true&max_price=100&ordering=price
```

**Success Response (200 OK):**
```json
{
    "count": 25,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Professional Oil Painting Brush Set",
            "description": "Premium quality brush set with 12 different sizes",
            "equipment_type": "brush",
            "price": "45.99",
            "stock_quantity": 50,
            "image": "http://localhost:8000/media/equipment/brush_set.jpg",
            "is_available": true,
            "created_at": "2025-10-01T10:00:00Z",
            "in_stock": true
        }
    ]
}
```

---

### 2. Get In-Stock Equipment
**Endpoint:** `GET /api/equipment/in-stock/`

---

## 📊 Dashboard & Analytics

### 1. Get Dashboard Stats
**Endpoint:** `GET /api/dashboard/stats/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
```

**Success Response (200 OK) - Artist:**
```json
{
    "user_type": "artist",
    "stats": {
        "total_earnings": "45000.00",
        "total_projects_completed": 120,
        "active_bids": 5,
        "pending_jobs": 3,
        "average_rating": 4.8,
        "total_reviews": 85,
        "completion_rate": 98.5,
        "artworks_uploaded": 45,
        "artworks_sold": 28
    }
}
```

**Success Response (200 OK) - Buyer:**
```json
{
    "user_type": "buyer",
    "stats": {
        "total_spent": "15000.00",
        "active_jobs": 2,
        "completed_jobs": 18,
        "total_jobs_posted": 20,
        "artworks_purchased": 12,
        "equipment_purchased": 25,
        "pending_orders": 1
    }
}
```

---

## 🔍 Global Search

### Search Endpoint
**Endpoint:** `GET /api/search/?q=keyword`

**Query Parameters:**
- `q`: Search keyword (required)

**Example Request:**
```
GET /api/search/?q=logo%20design
```

**Success Response (200 OK):**
```json
{
    "query": "logo design",
    "results": {
        "artworks": [
            {
                "id": 1,
                "title": "Modern Logo Design",
                "artist_name": "artist_john",
                "price": "299.99",
                "image": "http://localhost:8000/media/artworks/logo1.jpg"
            }
        ],
        "jobs": [
            {
                "id": 5,
                "title": "Logo Design for Tech Startup",
                "buyer_name": "buyer_sarah",
                "budget_min": "500.00",
                "budget_max": "1000.00",
                "status": "open"
            }
        ],
        "artists": [
            {
                "id": 1,
                "username": "artist_john",
                "full_name": "John Doe",
                "skills": "Logo Design, Branding, Adobe Illustrator",
                "rating": 4.8
            }
        ]
    },
    "total_results": 15
}
```

---

## 📝 Common Response Formats

### Success Response Structure
```json
{
    "data": { ... },
    "message": "Operation successful"
}
```

### Error Response Structure
```json
{
    "error": "Error message",
    "details": {
        "field_name": ["Error detail 1", "Error detail 2"]
    }
}
```

### Pagination Structure
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=3",
    "previous": "http://localhost:8000/api/endpoint/?page=1",
    "results": [ ... ]
}
```

---

## 🔒 Authentication Headers

For all authenticated endpoints, include:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

---

## 📤 File Upload Format

For endpoints that accept file uploads, use:
```
Content-Type: multipart/form-data
```

Example with cURL:
```bash
curl -X POST http://localhost:8000/api/artworks/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "title=Beautiful Sunset" \
  -F "description=A stunning sunset painting" \
  -F "category_id=1" \
  -F "artwork_type=digital" \
  -F "price=299.99" \
  -F "image=@/path/to/image.jpg"
```

---

## ⚠️ Common HTTP Status Codes

- **200 OK**: Successful GET, PUT, PATCH request
- **201 Created**: Successful POST request (resource created)
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid data or validation error
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: User doesn't have permission
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## 🎯 Quick Testing Examples

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_artist",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "user_type": "artist",
    "first_name": "Test",
    "last_name": "Artist"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_artist",
    "password": "TestPass123!"
  }'
```

**Get Artworks:**
```bash
curl -X GET "http://localhost:8000/api/artworks/?page=1&page_size=10"
```

**Create Bid:**
```bash
curl -X POST http://localhost:8000/api/bids/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 5,
    "bid_amount": "750.00",
    "delivery_time": 7,
    "cover_letter": "I can help with this project..."
  }'
```

---

## 📱 Testing with Postman

1. **Set Base URL**: `http://localhost:8000/api/`
2. **Create Environment Variable**: `token` = your auth token
3. **Set Authorization Header**: `Authorization: Token {{token}}`
4. **Use Pre-request Scripts** for dynamic data

---

## 🔄 Rate Limiting

- **Anonymous Users**: 100 requests/hour
- **Authenticated Users**: 1000 requests/hour
- **Admin Users**: Unlimited

---

## 📞 Support & Documentation

- **API Docs**: http://localhost:8000/api/docs/
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

---

---

## 📋 Complete API Endpoints Summary

### 🔐 Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login (with 2FA support)
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `PATCH /api/auth/profile/` - Partial update user profile

### 🔐 Two-Factor Authentication (2FA)
- `GET /api/auth/2fa/setup/` - Setup 2FA (get QR code)
- `POST /api/auth/2fa/enable/` - Enable 2FA
- `POST /api/auth/2fa/disable/` - Disable 2FA
- `POST /api/auth/2fa/verify/` - Verify 2FA code
- `GET /api/auth/2fa/status/` - Get 2FA status
- `POST /api/auth/2fa/backup-codes/` - Regenerate backup codes

### 👨‍🎨 Artist Profiles
- `GET /api/artist-profiles/` - List all artists
- `POST /api/artist-profiles/` - Create artist profile
- `GET /api/artist-profiles/{id}/` - Get artist details
- `PUT /api/artist-profiles/{id}/` - Update artist profile
- `PATCH /api/artist-profiles/{id}/` - Partial update artist profile
- `DELETE /api/artist-profiles/{id}/` - Delete artist profile
- `GET /api/artist-profiles/{id}/reviews/` - Get artist reviews
- `GET /api/artist-profiles/{id}/artworks/` - Get artist artworks

### 🛍️ Buyer Profiles
- `GET /api/buyer-profiles/` - List all buyers
- `POST /api/buyer-profiles/` - Create buyer profile
- `GET /api/buyer-profiles/{id}/` - Get buyer details
- `PUT /api/buyer-profiles/{id}/` - Update buyer profile
- `PATCH /api/buyer-profiles/{id}/` - Partial update buyer profile
- `DELETE /api/buyer-profiles/{id}/` - Delete buyer profile
- `GET /api/buyer-profiles/{id}/purchases/` - **🆕 Get buyer purchases**

### 📂 Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get category details

### 🎨 Artworks (with S3 & AI Duplicate Detection)
- `GET /api/artworks/` - List all artworks
- `POST /api/artworks/` - **🆕 Create artwork (S3 + AI duplicate check)**
- `GET /api/artworks/{id}/` - Get artwork details
- `PUT /api/artworks/{id}/` - **🆕 Update artwork (S3 support)**
- `PATCH /api/artworks/{id}/` - **🆕 Partial update artwork (S3 support)**
- `DELETE /api/artworks/{id}/` - **🆕 Delete artwork (S3 cleanup)**
- `POST /api/artworks/{id}/like/` - Like artwork
- `GET /api/artworks/featured/` - Get featured artworks

### 💼 Jobs/Projects
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create job
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `PATCH /api/jobs/{id}/` - Partial update job
- `DELETE /api/jobs/{id}/` - Delete job
- `GET /api/jobs/{id}/bids/` - Get job bids
- `POST /api/jobs/{id}/hire/` - Hire artist
- `POST /api/jobs/{id}/complete/` - Complete job

### 💰 Bids
- `GET /api/bids/` - List my bids
- `POST /api/bids/` - Create bid
- `GET /api/bids/{id}/` - Get bid details
- `PUT /api/bids/{id}/` - Update bid
- `PATCH /api/bids/{id}/` - Partial update bid
- `DELETE /api/bids/{id}/` - Delete bid

### 🛠️ Equipment
- `GET /api/equipment/` - List all equipment
- `POST /api/equipment/` - Create equipment
- `GET /api/equipment/{id}/` - Get equipment details
- `PUT /api/equipment/{id}/` - Update equipment
- `PATCH /api/equipment/{id}/` - Partial update equipment
- `DELETE /api/equipment/{id}/` - Delete equipment
- `GET /api/equipment/in-stock/` - Get in-stock equipment

### 📦 Orders
- `GET /api/orders/` - List my orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/` - Update order
- `PATCH /api/orders/{id}/` - Partial update order
- `DELETE /api/orders/{id}/` - Delete order
- `POST /api/orders/{id}/confirm/` - Confirm order
- `POST /api/orders/{id}/cancel/` - Cancel order

### 💳 Payments (with Stripe 3D Secure)
- `GET /api/payments/` - List my payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/{id}/` - Get payment details
- `POST /api/payments/{id}/process/` - Process payment (get client_secret)
- `POST /api/payments/{id}/confirm/` - Confirm payment with 3D Secure
- `POST /api/payments/{id}/3d-secure/` - Handle 3D Secure completion



### 💬 Messages
- `GET /api/messages/` - List my messages
- `POST /api/messages/` - Send message
- `GET /api/messages/{id}/` - Get message details
- `PUT /api/messages/{id}/` - Update message
- `PATCH /api/messages/{id}/` - Partial update message
- `DELETE /api/messages/{id}/` - Delete message
- `POST /api/messages/{id}/mark-read/` - Mark message as read
- `GET /api/messages/conversations/` - Get conversations

### ⭐ Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/{id}/` - Get review details
- `PUT /api/reviews/{id}/` - Update review
- `PATCH /api/reviews/{id}/` - Partial update review
- `DELETE /api/reviews/{id}/` - Delete review

### 📄 Contracts
- `GET /api/contracts/` - List my contracts
- `POST /api/contracts/` - Create contract
- `GET /api/contracts/{id}/` - Get contract details
- `PUT /api/contracts/{id}/` - Update contract
- `PATCH /api/contracts/{id}/` - Partial update contract
- `DELETE /api/contracts/{id}/` - Delete contract
- `POST /api/contracts/{id}/sign/` - Sign contract

### 🔔 Notifications
- `GET /api/notifications/` - List my notifications
- `GET /api/notifications/{id}/` - Get notification details
- `POST /api/notifications/{id}/mark-read/` - Mark notification as read
- `POST /api/notifications/mark-all-read/` - Mark all notifications as read
- `GET /api/notifications/unread-count/` - Get unread count

### 📊 Analytics (Admin only)
- `GET /api/analytics/` - List analytics
- `GET /api/analytics/{id}/` - Get analytics details
- `POST /api/analytics/calculate-today/` - Calculate today's analytics

### 🔍 Search & Dashboard
- `GET /api/search/?q=keyword` - Global search
- `GET /api/dashboard/stats/` - Get dashboard statistics

## �️ Admin APII Endpoints (🆕 NEW)

**Base URL:** `http://localhost:8000/api/admin/`

**Authentication Required:** All admin endpoints require admin/staff authentication
```
Authorization: Token YOUR_ADMIN_TOKEN
```

---

### 📊 Dashboard & Analytics

#### 1. Get Admin Dashboard Statistics
**Endpoint:** `GET /api/admin/dashboard/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "user_stats": {
        "total_users": 1250,
        "new_users_today": 15,
        "new_users_week": 89,
        "new_users_month": 342,
        "verified_users": 1100,
        "active_users": 1180,
        "artists": 450,
        "buyers": 800
    },
    "content_stats": {
        "total_artworks": 3500,
        "featured_artworks": 150,
        "pending_artworks": 12,
        "total_jobs": 890,
        "open_jobs": 45,
        "completed_jobs": 720,
        "total_categories": 8,
        "active_categories": 7
    },
    "financial_stats": {
        "total_revenue": "125000.50",
        "revenue_today": "2500.00",
        "revenue_week": "18750.25",
        "revenue_month": "45200.80",
        "pending_payments": 25,
        "total_orders": 1200,
        "pending_orders": 8
    },
    "activity_stats": {
        "total_bids": 2340,
        "pending_bids": 156,
        "total_messages": 8900,
        "unread_messages": 234,
        "total_reviews": 1890,
        "average_rating": 4.6,
        "total_contracts": 567,
        "active_contracts": 89
    },
    "recent_activity": {
        "recent_users": [
            {
                "id": 1251,
                "username": "new_artist_2024",
                "email": "artist@example.com",
                "user_type": "artist",
                "created_at": "2025-12-11T10:30:00Z"
            }
        ],
        "recent_artworks": [
            {
                "id": 3501,
                "title": "Digital Masterpiece",
                "artist__username": "top_artist",
                "price": "599.99",
                "created_at": "2025-12-11T09:15:00Z"
            }
        ],
        "recent_jobs": [
            {
                "id": 891,
                "title": "Logo Design Project",
                "buyer__username": "startup_buyer",
                "status": "open",
                "created_at": "2025-12-11T08:45:00Z"
            }
        ],
        "recent_payments": [
            {
                "id": 1201,
                "transaction_id": "TXN789456123",
                "payer__username": "buyer_sarah",
                "payee__username": "artist_john",
                "amount": "850.00",
                "status": "completed",
                "created_at": "2025-12-11T07:20:00Z"
            }
        ]
    },
    "generated_at": "2025-12-11T12:00:00Z"
}
```

---

#### 2. Get Revenue Report
**Endpoint:** `GET /api/admin/revenue-report/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD format, optional)
- `end_date`: End date (YYYY-MM-DD format, optional)

**Example Request:**
```
GET /api/admin/revenue-report/?start_date=2024-01-01&end_date=2024-12-31
```

**Success Response (200 OK):**
```json
{
    "date_range": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    "total_revenue": "125000.50",
    "total_transactions": 1200,
    "revenue_by_method": [
        {
            "payment_method": "stripe",
            "total": "75000.30",
            "count": 720
        },
        {
            "payment_method": "jazzcash",
            "total": "35000.20",
            "count": 350
        },
        {
            "payment_method": "bank_transfer",
            "total": "15000.00",
            "count": 130
        }
    ],
    "daily_revenue": [
        {
            "day": "2024-12-10",
            "total": "2500.00",
            "count": 15
        },
        {
            "day": "2024-12-11",
            "total": "3200.50",
            "count": 18
        }
    ],
    "top_artists": [
        {
            "payee__username": "top_artist_john",
            "total_earned": "15000.00",
            "payment_count": 45
        },
        {
            "payee__username": "expert_designer",
            "total_earned": "12500.50",
            "payment_count": 38
        }
    ],
    "top_buyers": [
        {
            "payer__username": "enterprise_buyer",
            "total_spent": "25000.00",
            "payment_count": 67
        },
        {
            "payer__username": "startup_client",
            "total_spent": "18750.25",
            "payment_count": 52
        }
    ]
}
```

---

### 👥 User Management

#### 1. List All Users (Admin View)
**Endpoint:** `GET /api/admin/users/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `user_type`: `artist`, `buyer`, or `admin`
- `is_verified`: `true` or `false`
- `is_active`: `true` or `false`
- `is_staff`: `true` or `false`
- `search`: Search in username, email, name
- `ordering`: `created_at`, `-created_at`, `username`, `last_login`
- `page`: Page number
- `page_size`: Items per page (default: 50, max: 200)

**Example Request:**
```
GET /api/admin/users/?user_type=artist&is_verified=false&ordering=-created_at&page=1
```

**Success Response (200 OK):**
```json
{
    "count": 450,
    "next": "http://localhost:8000/api/admin/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "artist_john",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "artist",
            "phone_number": "+923001234567",
            "is_verified": false,
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "profile_image": "http://localhost:8000/media/profiles/john.jpg",
            "created_at": "2025-10-12T10:30:00Z",
            "updated_at": "2025-12-11T08:15:00Z",
            "last_login": "2025-12-11T07:45:00Z",
            "total_artworks": 15,
            "total_jobs_posted": 0,
            "total_bids": 23,
            "total_spent": "0.00",
            "total_earned": "5600.00",
            "last_activity": "2025-12-11T07:45:00Z"
        }
    ]
}
```

---

#### 2. Verify User Account
**Endpoint:** `POST /api/admin/users/{id}/verify/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Example:** `POST /api/admin/users/1/verify/`

**Success Response (200 OK):**
```json
{
    "message": "User artist_john verified successfully",
    "user": {
        "id": 1,
        "username": "artist_john",
        "is_verified": true,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 3. Activate/Deactivate User
**Endpoint:** `POST /api/admin/users/{id}/activate/`
**Endpoint:** `POST /api/admin/users/{id}/deactivate/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "User artist_john activated successfully",
    "user": {
        "id": 1,
        "username": "artist_john",
        "is_active": true,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 4. Make User Staff
**Endpoint:** `POST /api/admin/users/{id}/make-staff/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "User artist_john is now staff",
    "user": {
        "id": 1,
        "username": "artist_john",
        "is_staff": true,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 5. Get User Statistics
**Endpoint:** `GET /api/admin/users/stats/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "total_users": 1250,
    "verified_users": 1100,
    "active_users": 1180,
    "artists": 450,
    "buyers": 800,
    "admins": 5,
    "staff_users": 12,
    "recent_registrations": 89
}
```

---

#### 6. Bulk User Actions
**Endpoint:** `POST /api/admin/bulk/users/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "user_ids": [1, 2, 3, 4, 5],
    "action": "verify"
}
```

**Available Actions:**
- `verify` - Verify selected users
- `unverify` - Unverify selected users
- `activate` - Activate selected users
- `deactivate` - Deactivate selected users
- `make_staff` - Make selected users staff
- `remove_staff` - Remove staff privileges

**Success Response (200 OK):**
```json
{
    "message": "5 users verified successfully",
    "affected_users": 5,
    "action": "verify",
    "processed_at": "2025-12-11T12:00:00Z"
}
```

---

### 🎨 Artwork Management

#### 1. List All Artworks (Admin View)
**Endpoint:** `GET /api/admin/artworks/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `artwork_type`: `digital`, `physical`, or `mixed`
- `is_available`: `true` or `false`
- `is_featured`: `true` or `false`
- `category`: Category ID
- `rekognition_checked`: `true` or `false`
- `search`: Search in title, description, artist name
- `ordering`: `created_at`, `-created_at`, `price`, `views_count`, `similarity_score`
- `page`: Page number
- `page_size`: Items per page

**Example Request:**
```
GET /api/admin/artworks/?is_available=false&rekognition_checked=true&ordering=-created_at
```

**Success Response (200 OK):**
```json
{
    "count": 3500,
    "next": "http://localhost:8000/api/admin/artworks/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Digital Masterpiece",
            "description": "A stunning digital artwork",
            "artist": 1,
            "artist_username": "artist_john",
            "artist_email": "john@example.com",
            "category": 1,
            "category_name": "Digital Art",
            "artwork_type": "digital",
            "price": "599.99",
            "is_available": false,
            "is_featured": true,
            "views_count": 1250,
            "likes_count": 89,
            "created_at": "2025-10-10T15:30:00Z",
            "updated_at": "2025-12-11T09:15:00Z",
            "s3_image_url": "https://bucket.s3.amazonaws.com/artworks/1/image.jpg",
            "s3_watermarked_url": "https://bucket.s3.amazonaws.com/artworks/1/watermarked.jpg",
            "rekognition_checked": true,
            "rekognition_labels": [
                {"name": "Art", "confidence": 99.5},
                {"name": "Digital", "confidence": 98.2}
            ],
            "similarity_score": "15.50",
            "duplicate_risk": "LOW",
            "moderation_status": "REJECTED"
        }
    ]
}
```

---

#### 2. Approve Artwork
**Endpoint:** `POST /api/admin/artworks/{id}/approve/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Example:** `POST /api/admin/artworks/1/approve/`

**Success Response (200 OK):**
```json
{
    "message": "Artwork \"Digital Masterpiece\" approved successfully",
    "artwork": {
        "id": 1,
        "title": "Digital Masterpiece",
        "is_available": true,
        "moderation_status": "APPROVED",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 3. Feature Artwork
**Endpoint:** `POST /api/admin/artworks/{id}/feature/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Artwork \"Digital Masterpiece\" featured successfully",
    "artwork": {
        "id": 1,
        "title": "Digital Masterpiece",
        "is_featured": true,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 4. Get Artwork Statistics
**Endpoint:** `GET /api/admin/artworks/stats/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "total_artworks": 3500,
    "available_artworks": 3200,
    "featured_artworks": 150,
    "pending_review": 12,
    "total_views": 2500000,
    "total_likes": 45000,
    "average_price": "425.75",
    "recent_uploads": 89
}
```

---

#### 5. Bulk Artwork Actions
**Endpoint:** `POST /api/admin/bulk/artworks/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "artwork_ids": [1, 2, 3, 4, 5],
    "action": "approve"
}
```

**Available Actions:**
- `approve` - Approve selected artworks
- `reject` - Reject selected artworks
- `feature` - Feature selected artworks
- `unfeature` - Unfeature selected artworks

**Success Response (200 OK):**
```json
{
    "message": "5 artworks approved successfully",
    "affected_artworks": 5,
    "action": "approve",
    "processed_at": "2025-12-11T12:00:00Z"
}
```

---

### 💼 Job Management

#### 1. List All Jobs (Admin View)
**Endpoint:** `GET /api/admin/jobs/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `status`: `open`, `in_progress`, `completed`, or `cancelled`
- `experience_level`: `entry`, `intermediate`, or `expert`
- `category`: Category ID
- `search`: Search in title, description, buyer name
- `ordering`: `created_at`, `-created_at`, `budget_min`, `deadline`
- `page`: Page number
- `page_size`: Items per page

**Success Response (200 OK):**
```json
{
    "count": 890,
    "next": "http://localhost:8000/api/admin/jobs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 5,
            "title": "Logo Design for Tech Startup",
            "description": "Need a modern, minimalist logo design...",
            "buyer": 2,
            "buyer_username": "startup_buyer",
            "buyer_email": "buyer@startup.com",
            "hired_artist": 1,
            "hired_artist_username": "artist_john",
            "category": 2,
            "category_name": "Graphic Design",
            "budget_min": "500.00",
            "budget_max": "1000.00",
            "duration_days": 7,
            "required_skills": "Logo Design, Branding",
            "experience_level": "expert",
            "status": "in_progress",
            "final_amount": "750.00",
            "deadline": "2025-12-20T23:59:59Z",
            "created_at": "2025-12-05T08:00:00Z",
            "updated_at": "2025-12-10T14:30:00Z",
            "total_bids": 8,
            "average_bid": "725.50",
            "days_since_posted": 6,
            "days_until_deadline": 9
        }
    ]
}
```

---

#### 2. Close Job (Admin Action)
**Endpoint:** `POST /api/admin/jobs/{id}/close/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Job \"Logo Design for Tech Startup\" closed by admin",
    "job": {
        "id": 5,
        "title": "Logo Design for Tech Startup",
        "status": "cancelled",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 3. Get Job Statistics
**Endpoint:** `GET /api/admin/jobs/stats/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "total_jobs": 890,
    "open_jobs": 45,
    "in_progress_jobs": 89,
    "completed_jobs": 720,
    "cancelled_jobs": 36,
    "average_budget": {
        "avg_min": "425.75",
        "avg_max": "850.50"
    },
    "total_bids": 2340,
    "recent_jobs": 23
}
```

---

### 💳 Payment Management

#### 1. List All Payments (Admin View)
**Endpoint:** `GET /api/admin/payments/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Query Parameters:**
- `payment_method`: `stripe`, `jazzcash`, `bank_transfer`, `cash_on_delivery`
- `status`: `pending`, `completed`, `failed`, `refunded`
- `hire_status`: `pending`, `released`, `cancelled`
- `search`: Search in transaction ID, payer, payee
- `ordering`: `created_at`, `-created_at`, `amount`
- `page`: Page number
- `page_size`: Items per page

**Success Response (200 OK):**
```json
{
    "count": 1200,
    "next": "http://localhost:8000/api/admin/payments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "transaction_id": "TXN789456123",
            "payer": 2,
            "payer_username": "buyer_sarah",
            "payee": 1,
            "payee_username": "artist_john",
            "order": null,
            "job": 5,
            "job_title": "Logo Design for Tech Startup",
            "amount": "750.00",
            "payment_method": "stripe",
            "status": "completed",
            "hire_status": "pending",
            "stripe_payment_intent": "pi_1234567890",
            "created_at": "2025-12-10T14:30:00Z",
            "platform_fee": "75.00",
            "artist_earning": "675.00",
            "days_since_payment": 1
        }
    ]
}
```

---

#### 2. Release Payment to Artist
**Endpoint:** `POST /api/admin/payments/{id}/release/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Payment TXN789456123 released to artist",
    "payment": {
        "id": 1,
        "transaction_id": "TXN789456123",
        "hire_status": "released",
        "artist_earning": "675.00",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 3. Process Refund
**Endpoint:** `POST /api/admin/payments/{id}/refund/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Payment TXN789456123 refunded successfully",
    "payment": {
        "id": 1,
        "transaction_id": "TXN789456123",
        "status": "refunded",
        "refund_amount": "750.00",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 4. Get Payment Statistics
**Endpoint:** `GET /api/admin/payments/stats/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "total_payments": 1200,
    "completed_payments": 1050,
    "pending_payments": 120,
    "failed_payments": 25,
    "refunded_payments": 5,
    "total_revenue": "125000.50",
    "platform_fees": "12500.05",
    "pending_releases": 89
}
```

---

### 📂 Category Management

#### 1. Create Category
**Endpoint:** `POST /api/admin/categories/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "3D Modeling",
    "description": "3D modeling and rendering services",
    "is_active": true
}
```

**Success Response (201 Created):**
```json
{
    "id": 9,
    "name": "3D Modeling",
    "description": "3D modeling and rendering services",
    "is_active": true,
    "created_at": "2025-12-11T12:00:00Z"
}
```

---

#### 2. Activate/Deactivate Category
**Endpoint:** `POST /api/admin/categories/{id}/activate/`
**Endpoint:** `POST /api/admin/categories/{id}/deactivate/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Category \"3D Modeling\" activated successfully",
    "category": {
        "id": 9,
        "name": "3D Modeling",
        "is_active": true,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

### 🛠️ Equipment Management

#### 1. Update Equipment Stock
**Endpoint:** `POST /api/admin/equipment/{id}/update-stock/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "stock_quantity": 75
}
```

**Success Response (200 OK):**
```json
{
    "message": "Stock updated for \"Professional Brush Set\"",
    "equipment": {
        "id": 1,
        "name": "Professional Brush Set",
        "stock_quantity": 75,
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

### 📦 Order Management

#### 1. Force Complete Order
**Endpoint:** `POST /api/admin/orders/{id}/force-complete/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Order #1 marked as delivered by admin",
    "order": {
        "id": 1,
        "status": "delivered",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

#### 2. Cancel Order (Admin Action)
**Endpoint:** `POST /api/admin/orders/{id}/cancel/`

**Headers:**
```
Authorization: Token YOUR_ADMIN_TOKEN
```

**Success Response (200 OK):**
```json
{
    "message": "Order #1 cancelled by admin",
    "order": {
        "id": 1,
        "status": "cancelled",
        "updated_at": "2025-12-11T12:00:00Z"
    }
}
```

---

### ⚠️ Admin Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Invalid token or authentication credentials not provided"
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action. Admin access required."
}
```

**404 Not Found:**
```json
{
    "detail": "User not found"
}
```

**400 Bad Request:**
```json
{
    "error": "Invalid action specified",
    "available_actions": ["verify", "unverify", "activate", "deactivate", "make_staff", "remove_staff"]
}
```

---

## 🚀 Frontend Implementation Guide

### 1. **Authentication Flow**
```javascript
// Register
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
};

// Login
const loginUser = async (credentials) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
};

// Authenticated requests
const authHeaders = {
  'Authorization': `Token ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
};
```

### 2. **Admin Dashboard Implementation** 🆕
```javascript
// Fetch admin dashboard stats
const fetchAdminStats = async () => {
  const response = await fetch('/api/admin/dashboard/', {
    headers: authHeaders
  });
  return response.json();
};

// Example admin dashboard data
const adminStats = {
  user_stats: {
    total_users: 1250,
    new_users_today: 15,
    verified_users: 1100,
    artists: 450,
    buyers: 800
  },
  financial_stats: {
    total_revenue: 125000.50,
    revenue_today: 2500.00,
    pending_payments: 25
  },
  content_stats: {
    total_artworks: 3500,
    pending_artworks: 12,
    featured_artworks: 150
  }
};

// Bulk user actions
const bulkUserAction = async (userIds, action) => {
  const response = await fetch('/api/admin/bulk/users/', {
    method: 'POST',
    headers: authHeaders,
    body: JSON.stringify({
      user_ids: userIds,
      action: action // 'verify', 'activate', 'deactivate', etc.
    })
  });
  return response.json();
};

// Revenue report with date filtering
const fetchRevenueReport = async (startDate, endDate) => {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });
  const response = await fetch(`/api/admin/revenue-report/?${params}`, {
    headers: authHeaders
  });
  return response.json();
};
```

### 3. **Content Moderation Implementation** 🆕
```javascript
// Approve artwork
const approveArtwork = async (artworkId) => {
  const response = await fetch(`/api/admin/artworks/${artworkId}/approve/`, {
    method: 'POST',
    headers: authHeaders
  });
  return response.json();
};

// Feature artwork
const featureArtwork = async (artworkId) => {
  const response = await fetch(`/api/admin/artworks/${artworkId}/feature/`, {
    method: 'POST',
    headers: authHeaders
  });
  return response.json();
};

// Bulk artwork actions
const bulkArtworkAction = async (artworkIds, action) => {
  const response = await fetch('/api/admin/bulk/artworks/', {
    method: 'POST',
    headers: authHeaders,
    body: JSON.stringify({
      artwork_ids: artworkIds,
      action: action // 'approve', 'reject', 'feature', 'unfeature'
    })
  });
  return response.json();
};
```

### 4. **Payment Management Implementation** 🆕
```javascript
// Release payment to artist
const releasePayment = async (paymentId) => {
  const response = await fetch(`/api/admin/payments/${paymentId}/release/`, {
    method: 'POST',
    headers: authHeaders
  });
  return response.json();
};

// Process refund
const refundPayment = async (paymentId) => {
  const response = await fetch(`/api/admin/payments/${paymentId}/refund/`, {
    method: 'POST',
    headers: authHeaders
  });
  return response.json();
};

// Get payment statistics
const fetchPaymentStats = async () => {
  const response = await fetch('/api/admin/payments/stats/', {
    headers: authHeaders
  });
  return response.json();
};
```

### 5. **Buyer Purchases Tab Implementation**
```javascript
// Fetch buyer purchases
const fetchBuyerPurchases = async (buyerId) => {
  const response = await fetch(`/api/buyer-profiles/${buyerId}/purchases/`, {
    headers: { 'Authorization': `Token ${localStorage.getItem('token')}` }
  });
  return response.json();
};

// Display purchases in UI
const displayPurchases = (purchasesData) => {
  const { orders, payments, total_orders, total_payments } = purchasesData;
  
  // Display orders (artwork/equipment purchases)
  orders.forEach(order => {
    console.log(`Order #${order.id}: ${order.order_type} - PKR${order.total_amount}`);
  });
  
  // Display payments (job payments to artists)
  payments.forEach(payment => {
    console.log(`Payment #${payment.id}: ${payment.job?.title} - PKR${payment.amount}`);
  });
};
```

### 3. **Artwork Upload with S3**
```javascript
// Upload artwork with automatic S3 storage and duplicate detection
const uploadArtwork = async (formData) => {
  const response = await fetch('/api/artworks/', {
    method: 'POST',
    headers: { 'Authorization': `Token ${localStorage.getItem('token')}` },
    body: formData // FormData with image file
  });
  
  const result = await response.json();
  
  if (result.duplicate_detected) {
    alert(`Duplicate detected! Similarity: ${result.similarity_score}%`);
    return;
  }
  
  console.log('Artwork uploaded successfully:', result.artwork);
  console.log('AI Labels detected:', result.rekognition_labels);
};
```

### 4. **Real-time Features**
```javascript
// Fetch unread notifications count
const getUnreadCount = async () => {
  const response = await fetch('/api/notifications/unread-count/', {
    headers: authHeaders
  });
  const data = await response.json();
  updateNotificationBadge(data.unread_count);
};

// Fetch dashboard stats
const getDashboardStats = async () => {
  const response = await fetch('/api/dashboard/stats/', {
    headers: authHeaders
  });
  return response.json();
};
```

### 5. **Error Handling**
```javascript
const handleApiError = (response) => {
  if (response.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (response.status === 403) {
    alert('You do not have permission to perform this action');
  } else if (response.status === 400) {
    // Handle validation errors
    response.json().then(data => {
      console.error('Validation errors:', data);
    });
  }
};
```

---

## 🎯 Key Features for Frontend

### ✅ **Core Platform Features**
- **User Authentication** (Register, Login, Profile management, **2FA Support**)
- **Artist Profiles** (Complete CRUD, reviews, artworks)
- **Buyer Profiles** (Complete CRUD, **purchases history**)
- **Artworks** (S3 storage, AI duplicate detection, watermarking)
- **Jobs/Projects** (Complete job posting and bidding system)
- **Orders & Payments** (Complete e-commerce functionality)
- **Messages** (Real-time messaging system)
- **Reviews & Ratings** (Complete review system)
- **Contracts** (Digital contract signing)
- **Notifications** (Real-time notifications)
- **Search** (Global search across all content)
- **Dashboard** (Comprehensive statistics)

### 🛡️ **Admin Backend System** 🆕 **NEW**
- **👥 User Management** - Verify, activate, manage all user accounts with bulk operations
- **🎨 Content Moderation** - Approve/reject artworks, feature content, AI duplicate monitoring
- **💳 Payment Oversight** - Process refunds, release hire payments, monitor transactions
- **💼 Job Management** - Admin controls for jobs, projects, and bidding system
- **📊 Analytics Dashboard** - Real-time platform statistics and comprehensive reports
- **📈 Revenue Reports** - Detailed financial analytics with date filtering and trends
- **⚡ Bulk Operations** - Efficient mass actions for users, artworks, and content
- **🔐 Security Controls** - Role-based permissions, audit logging, and access management
- **🎛️ Professional Admin UI** - Enhanced Django admin with quick actions and modern interface

### 🆕 **Latest Major Updates**
- **🛡️ Complete Admin Backend** - Full platform management and oversight system
- **📊 Real-time Analytics** - Live dashboard with comprehensive platform statistics
- **💳 Advanced Payment Management** - Admin controls for refunds, releases, and monitoring
- **👥 Bulk User Operations** - Efficient mass actions for user verification and management
- **🎨 Content Moderation System** - Artwork approval workflow with AI duplicate detection
- **📈 Financial Reporting** - Detailed revenue analytics with custom date ranges
- **🔐 Enhanced Security** - Role-based permissions and comprehensive audit trails
- **⚡ Performance Optimizations** - Bulk operations and efficient database queries
- **Buyer Purchases API** - Complete purchase history tracking and analytics
- **S3 Cloud Storage** - All images stored securely in AWS S3 with CDN delivery
- **AI Duplicate Detection** - Advanced plagiarism prevention using AWS Rekognition
- **Automatic Watermarking** - Intelligent copyright protection for artist content

---

## �️ eAdmin Access Quick Guide

### 🚀 Setup Admin System
```bash
# 1. Create admin users and sample data
python manage.py setup_admin --create-superuser --create-sample-data

# 2. Start the server
python manage.py runserver

# 3. Access admin interfaces
```

### 🔗 Admin URLs
- **Django Admin Panel**: `http://localhost:8000/admin/`
- **API Dashboard**: `http://localhost:8000/api/admin/dashboard/`
- **Revenue Reports**: `http://localhost:8000/api/admin/revenue-report/`

### 🔑 Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@artconnect.com`

### 📊 Admin API Examples
```bash
# Get dashboard statistics
curl -H "Authorization: Token YOUR_ADMIN_TOKEN" \
     http://localhost:8000/api/admin/dashboard/

# Verify multiple users
curl -X POST -H "Authorization: Token YOUR_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"user_ids": [1,2,3], "action": "verify"}' \
     http://localhost:8000/api/admin/bulk/users/

# Get revenue report
curl -H "Authorization: Token YOUR_ADMIN_TOKEN" \
     "http://localhost:8000/api/admin/revenue-report/?start_date=2024-01-01&end_date=2024-12-31"
```

---

## 📞 Developer Support

**Full Stack Engineer:** Shoaib Shoukat  
**API Documentation:** Complete and ready for frontend implementation  
**Admin System:** Comprehensive backend management with professional UI  
**Testing:** All endpoints tested and functional  
**Deployment:** Ready for production deployment with admin controls  

---

**Note:** Replace `localhost:8000` with your actual server URL in production.