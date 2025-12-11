# 🎯 CultureUp - Complete API Documentation

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
1. [Authentication](#authentication)
2. [Artist Profiles](#artist-profiles)
3. [Buyer Profiles](#buyer-profiles)
4. [Artworks (with S3 & Rekognition)](#artworks)
5. [Jobs/Projects](#jobs-projects)
6. [Bids](#bids)
7. [Orders](#orders)
8. [Payments](#payments)
9. [Messages](#messages)
10. [Reviews](#reviews)
11. [Contracts](#contracts)
12. [Notifications](#notifications)

---

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

### 1. Create Buyer Profile
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

### 2. Update Buyer Profile
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

### 3. Process Payment
**Endpoint:** `POST /api/payments/{id}/process/`

**Headers:**
```
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
    "transaction_id": "JC1234567890"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Payment processed successfully",
    "payment": {
        "id": 1,
        "status": "completed",
        "transaction_id": "JC1234567890"
    }
}
```

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

**Note:** Replace `localhost:8000` with your actual server URL in production.