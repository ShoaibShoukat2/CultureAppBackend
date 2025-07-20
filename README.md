# 🎨 User Authentication & Artist Profile API - Django REST Framework

This project provides a RESTful API for user authentication (sign up/sign in) and managing artist profiles. It uses Django, Django REST Framework, and Token Authentication.

---

## 📦 Features

- User registration (Sign up)
- User login (Sign in) with token generation
- Token-based authentication
- Artist profile creation and listing
- Profile metrics like completion rate, total earnings, etc.

---

## 🚀 API Endpoints

All endpoints are prefixed with: `/api/`

### 🔐 Authentication

#### ▶️ Sign Up (User Registration)
**URL**: `/api/signup/`  
**Method**: `POST`  
**Body Parameters** (JSON):
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "user_type": "artist",
  "phone_number": "1234567890",
  "profile_image": "http://example.com/image.jpg"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "user_type": "artist",
  "phone_number": "1234567890",
  "profile_image": "http://example.com/image.jpg"
}
```

---

#### ▶️ Sign In (User Login)
**URL**: `/api/signin/`  
**Method**: `POST`  
**Body Parameters** (JSON):
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response**:
```json
{
  "token": "your-auth-token",
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

---

## 🎨 Artist Profile

> All Artist Profile APIs require **Token Authentication** via `Authorization: Token <your-token>` header.

#### ▶️ Get Artist Profile List / Detail
**URL**: `/api/artist-profiles/`  
**Method**: `GET`

**Response**:
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "bio": "Digital painter and concept artist.",
    "skills": "Photoshop, Illustrator, Sketch",
    "experience_level": "expert",
    "hourly_rate": "25.00",
    "portfolio_description": "Worked with multiple gaming studios.",
    "rating": 4.9,
    "total_projects_completed": 35,
    "total_earnings": "5000.00",
    "is_available": true,
    "completion_rate": 95.0
  }
]
```

---

